from pickle import FROZENSET

from rest_framework import status, views, permissions, serializers, filters
from app.management.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from app.models import CustomUser
from app.serializers import CustomUserSerializer
from tracking.models import UserScreenshots
from utils.Qbkafka import QbKafkaProducer
from utils.common import ResponseFormat, get_all_reporting_users
import datetime
from rest_framework.pagination import PageNumberPagination
from utils.views import CustomModelViewSet


class Pagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

#todo: Active Inactive count API
class ActiveInactiveCountView(CustomModelViewSet):
    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticated]

    serializer_class = CustomUserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'phone_number', 'last_name', 'first_name']

    pagination_class = Pagination

    def __init__(self, **kwargs):
        self.response_format = ResponseFormat().response
        super().__init__(**kwargs)

    # def get_queryset(self):
    #     user = self.request.user
    #     return user.subordinates.all()

    def list(self, request, *args, **kwargs):

        mode = request.GET.get('mode', '')
        if mode == 'all':
            all_user_queryset = CustomUser.objects.all()
            all_users_serializer = self.get_serializer(all_user_queryset, many=True)
            self.response_format['status'] = True
            self.response_format['data'] = all_users_serializer.data
            return Response(self.response_format, status=status.HTTP_200_OK)

        queryset = self.filter_queryset(self.get_queryset())

        user = request.user.groups.first().permissions.filter(content_type__model='customuser').values_list('codename',
                                                                                                            flat=True)
        base_permissions = [permission.split('_')[0] for permission in user]

        # active_count = 0
        # inactive_count = 0


        if 'all' in base_permissions:
            all_user_queryset = CustomUser.objects.all()
            all_users_serializer = self.get_serializer(all_user_queryset, many=True)

            active_count = CustomUser.objects.filter(is_screenshot_active=True).count()
            inactive_count = CustomUser.objects.filter(is_screenshot_active=False).count()

            response_data = {
                'users': all_users_serializer.data,
                'active_count': active_count if active_count else 0,
                'inactive_count': inactive_count if inactive_count else 0,
            }

            self.response_format['status'] = True
            self.response_format['data'] = response_data
            return Response(self.response_format, status=status.HTTP_200_OK)

        elif 'team' in base_permissions:
            # team_user_queryset = request.user.subordinates.all()
            reporting_user = get_all_reporting_users(request.user)
            # reporting_user = [i.email for i in reporting_user]

            team_users_serializer = self.get_serializer(reporting_user, many=True)


            team_user_queryset_email = [i.email for i in reporting_user]
            team_user_queryset = CustomUser.objects.filter(email__in=team_user_queryset_email)

            active_count = team_user_queryset.filter(is_screenshot_active=True).count()
            inactive_count = team_user_queryset.filter(is_screenshot_active=False).count()

            response_data = {
                'users': team_users_serializer.data,
                'active_count': active_count if active_count else 0,
                'inactive_count': inactive_count if inactive_count else 0,
            }

            self.response_format['status'] = True
            self.response_format['data'] = response_data

            return Response(self.response_format, status=status.HTTP_200_OK)

        elif 'owned' in base_permissions:
            owned_user_queryset = CustomUser.objects.filter(id=request.user.id)
            owned_user_serializer = self.get_serializer(owned_user_queryset, many=True)

            active_count = CustomUser.objects.filter(id=request.user.id, is_screenshot_active=True).count()
            inactive_count = CustomUser.objects.filter(id=request.user.id, is_screenshot_active=False).count()

            response_data = {
                'users': owned_user_serializer.data,
                'active_count': active_count if active_count else 0,
                'inactive_count': inactive_count if inactive_count else 0,
            }

            self.response_format['status'] = True
            self.response_format['data'] = response_data

            return Response(self.response_format, status=status.HTTP_200_OK)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        all_data = serializer.data

        for index, data in enumerate(all_data):
            data['index'] = index + 1

        self.response_format['status'] = True
        self.response_format['data'] = all_data
        return Response(self.response_format, status=status.HTTP_200_OK)
