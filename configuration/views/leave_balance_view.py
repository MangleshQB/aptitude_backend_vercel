from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db.models import Q
from app.models import CustomUser
from rest_framework.response import Response

from configuration.models import LeaveBalance
from configuration.serializers import LeaveBalanceSerializer
from utils.common import ResponseFormat, get_all_reporting_users
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination


class Pagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class LeaveBalanceViewSet(APIView):
    queryset = LeaveBalance.objects.all()
    permission_classes = [IsAuthenticated]
    # pagination_class = Pagination

    def __init__(self, **kwargs):
        self.response_format = ResponseFormat().response
        super().__init__(**kwargs)

    def get(self, request):
        # user = list(request.user.groups.first().permissions.values_list('content_type__model', flat=True)
        # print()

        permissions = request.user.groups.all().first().permissions.filter(
            content_type__model='leavebalance').values_list('codename', flat=True)

        base_permissions = [permission.split('_')[0] for permission in permissions]
        print('LeaveBalanceViewSet base_permissions ->', base_permissions)

        if 'all' in base_permissions:
            all_user_queryset = LeaveBalance.objects.all()
            # print("LeaveBalanceViewSet all_user_queryset", all_user_queryset)

            all_users_serializer = LeaveBalanceSerializer(all_user_queryset, many=True)

            self.response_format['status'] = True
            self.response_format['data'] = all_users_serializer.data
            return Response(self.response_format, status=status.HTTP_200_OK)

            # return Response(all_users_serializer.data, status=status.HTTP_200_OK)

        if 'team' in base_permissions:
            # team_user_queryset = request.user.subordinates.all()
            team_user_queryset = get_all_reporting_users(request.user)

            print("LeaveBalanceViewSet all_user_queryset", team_user_queryset)
            leave_balance = LeaveBalance.objects.filter(user__in=team_user_queryset)
            team_users_serializer = LeaveBalanceSerializer(leave_balance, many=True)

            self.response_format['status'] = True
            self.response_format['data'] = team_users_serializer.data
            return Response(self.response_format, status=status.HTTP_200_OK)

        if 'owned' in base_permissions:
            owned_user_queryset = LeaveBalance.objects.filter(user__email=request.user.email)

            print("LeaveBalanceViewSet all_user_queryset", owned_user_queryset)

            owned_user_serializer = LeaveBalanceSerializer(owned_user_queryset, many=True)

            self.response_format['status'] = True
            self.response_format['data'] = owned_user_serializer.data
            return Response(self.response_format, status=status.HTTP_200_OK)
