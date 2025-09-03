from datetime import datetime, timedelta
from rest_framework.views import APIView
from django.contrib.auth.models import Permission
from rest_framework import status
from rest_framework.response import Response

from app.models import CustomUser
from tracking.serializer import UserScreenshotCountSerializer, UserScreenshotSerializer
from tracking.models import UserScreenshots
from utils.common import ResponseFormat, get_all_reporting_users
from utils.middlewares import CheckUser
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.authentication import TokenAuthentication
from rest_framework import permissions


class UserScreenshotView(APIView):
    serializer_class = UserScreenshotSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ["email", "created_at"]

    # authentication_classes = [TokenAuthentication]

    def __init__(self, **kwargs):
        self.response_format = ResponseFormat().response
        super().__init__(**kwargs)

    def get(self, request, *args, **kwargs):

        email = request.GET.get('email', '')
        # created_at = request.GET.get('date', '')
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 25))
        # page_size = 10
        start_date = request.GET.get('start_date', '')
        if start_date:
            start_date = datetime.strptime(start_date, "%d/%m/%Y").date()
        end_date = request.GET.get('end_date', '')
        if end_date:
            end_date = datetime.strptime(end_date, "%d/%m/%Y").date()
        screenshots = None
        is_email_accessible = False

        permissions = request.user.groups.all().first().permissions.filter(
            content_type__model='userscreenshots').values_list('codename', flat=True)

        base_permissions = [permission.split('_')[0] for permission in permissions]

        # team = request.user.subordinates.values_list('email', flat=True)
        team = [i.email for i in  get_all_reporting_users(request.user)]

        if email:
            if 'all' in base_permissions:
                if start_date and end_date:
                    screenshots = UserScreenshots.objects.filter(user__email=email, created_at__range=[start_date,
                                                                                                       end_date + timedelta(
                                                                                                           days=1)])
                else:
                    screenshots = UserScreenshots.objects.filter(user__email=email,
                                                                 created_at__date=datetime.now().date())
                is_email_accessible = True

            if 'team' in base_permissions:

                if email in team:

                    if start_date and end_date:
                        screenshots = UserScreenshots.objects.filter(user__email=email, created_at__range=[start_date,
                                                                                                           end_date + timedelta(
                                                                                                               days=1)])
                    else:
                        screenshots = UserScreenshots.objects.filter(user__email=email,
                                                                     created_at__date=datetime.now().date())
                    is_email_accessible = True

            if 'owned' in base_permissions:

                if request.user.email == email:

                    if start_date and end_date:
                        screenshots = UserScreenshots.objects.filter(user__email=email, created_at__range=[start_date,
                                                                                                           end_date + timedelta(
                                                                                                               days=1)])
                    else:
                        screenshots = UserScreenshots.objects.filter(user__email=email,
                                                                     created_at__date=datetime.now().date())
            get_name = CustomUser.objects.filter(email=email).values('first_name', 'last_name', 'email').first()

            # if screenshots or is_email_accessible:
            #
            #     serializer = self.serializer_class(screenshots, many=True)
            #
            #     self.response_format['data'] = serializer.data
            #     self.response_format['status'] = True
            #     return Response(self.response_format, status=status.HTTP_200_OK)
            if screenshots or is_email_accessible:
                total_items = screenshots.count()
                start_index = (page - 1) * page_size
                end_index = start_index + page_size
                paginated_screenshots = screenshots[start_index:end_index]

                serializer = self.serializer_class(paginated_screenshots, many=True)

                self.response_format['data'] = {
                    'count': total_items,
                    'page': page,
                    'page_size': page_size,
                    'first_name': get_name['first_name'],
                    'last_name': get_name['last_name'],
                    'email': get_name['email'],
                    'results': serializer.data,
                    'next': page + 1 if end_index < total_items else None,
                    'previous': page - 1 if page > 1 else None,
                }
                self.response_format['status'] = True
                return Response(self.response_format, status=status.HTTP_200_OK)

            else:

                self.response_format['error'] = "You don't have access to this email!"
                self.response_format['status'] = False
                return Response(self.response_format, status=status.HTTP_200_OK)

        self.response_format['error'] = 'Email Required'
        self.response_format['status'] = False
        return Response(self.response_format, status=status.HTTP_200_OK)
