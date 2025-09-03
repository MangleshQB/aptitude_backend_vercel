from calendar import monthrange
from rest_framework.views import APIView
from app.models import CustomUser
from utils.common import ResponseFormat, get_all_reporting_users
from rest_framework.response import Response
from rest_framework import status
from tracking.serializer import UserSoftwareUsageSerializer, GetUserSoftwareUsageSerializer, GetSoftwareDetailsSerializer
from tracking.models import UserSoftwareUsage
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.db.models import Count, Sum
from datetime import datetime, timedelta, date


class UserSoftwareUsageView(APIView):
    serializer_class = UserSoftwareUsageSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def __init__(self, **kwargs):
        self.response_format = ResponseFormat().response
        super().__init__(**kwargs)

    def post(self, request, *args, **kwargs):
        data = request.data

        serializer = self.serializer_class(data=request.data, context={'user': request.user})

        if serializer.is_valid(raise_exception=True):
            serializer.save()

            self.response_format['data'] = serializer.data
            self.response_format['status'] = True
            return Response(self.response_format, status=status.HTTP_200_OK)

        self.response_format['status'] = False
        self.response_format['error'] = serializer.errors
        return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)


class GetUserSoftwareUsage(APIView):
    serializer_class = GetUserSoftwareUsageSerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        self.response_format = ResponseFormat().response
        super().__init__(**kwargs)

    def post(self, request, *args, **kwargs):


        serializer = GetUserSoftwareUsageSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            start_date = serializer.validated_data.get('start_date')
            end_date = serializer.validated_data.get('end_date')
            email = serializer.validated_data.get('email')

            permissions = request.user.groups.all().first().permissions.filter(
                content_type__model='customuser').values_list('codename', flat=True)

            base_permissions = [permission.split('_')[0] for permission in permissions]
            reporting_user = get_all_reporting_users(request.user)
            team = [i.email for i in reporting_user]

            if 'all' in base_permissions:
                pass
            elif 'team' in base_permissions:
                if not email in team:
                    self.response_format['status'] = False
                    self.response_format['error'] = 'user have not permission'
                    return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)
            elif 'owned' in base_permissions:
                if not request.user.email == email:
                    self.response_format['status'] = False
                    self.response_format['error'] = 'user have not permission'
                    return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)

            else:
                self.response_format['status'] = False
                self.response_format['error'] = 'user have not permission'
                return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)

            usages_count = list(UserSoftwareUsage.objects.filter(
                user__email=email,
                start_time__gte=start_date,
                end_time__lte=end_date + timedelta(days=1),

            ).values('software_process__name', 'software_process__icon', 'software_process__os_type',
                     'software_process__display_name').annotate(
                usage_count=Sum('total_usage')))

            total_usage = UserSoftwareUsage.objects.filter(
                user__email=email,
                start_time__gte=start_date,
                end_time__lte=end_date + timedelta(days=1),
            ).aggregate(total_usage=Sum('total_usage'))

            user_name = CustomUser.objects.filter(email=email).values('first_name', 'last_name').first()

            self.response_format['data'] = usages_count
            self.response_format['name'] = user_name
            self.response_format['total_usage'] = total_usage['total_usage']
            self.response_format['status'] = True
            return Response(self.response_format, status=status.HTTP_200_OK)

        self.response_format['status'] = False
        self.response_format['error'] = serializer.errors
        return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)


def get_month_range(year, month):
    start_date = date(year, month, 1)
    end_date = date(year, month, monthrange(year, month)[1])
    return start_date, end_date


def get_week_range(input_date):
    start_of_week = input_date - timedelta(days=input_date.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    return start_of_week, end_of_week


class GetUserSoftwareUsageReport(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        self.response_format = ResponseFormat().response
        super().__init__(**kwargs)

    def get(self, request, *args, **kwargs):

        type = request.GET.get('type', None)
        email = request.GET.get('email', '')

        if email:

            if type == 'monthly':
                start_date, end_date = get_month_range(month=date.today().month, year=date.today().year)
            elif type == 'weekly':
                start_date, end_date = get_week_range(date.today())
            elif type == 'yearly':
                start_date = date(day=1, month=1, year=date.today().year)
                end_date = date(day=31, month=12, year=date.today().year)
            else:
                start_date = date.today()
                end_date = date.today()

            permissions = request.user.groups.all().first().permissions.filter(
                content_type__model='customuser').values_list('codename', flat=True)

            base_permissions = [permission.split('_')[0] for permission in permissions]
            reporting_user = get_all_reporting_users(request.user)
            team = [i.email for i in reporting_user]

            if 'all' in base_permissions:
                pass
            elif 'team' in base_permissions:
                if not email in team:
                    self.response_format['status'] = False
                    self.response_format['error'] = 'user have not permission'
                    return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)
            elif 'owned' in base_permissions:
                if not request.user.email == email:
                    self.response_format['status'] = False
                    self.response_format['error'] = 'user have not permission'
                    return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)

            else:
                self.response_format['status'] = False
                self.response_format['error'] = 'user have not permission'
                return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)


            usages_count = list(UserSoftwareUsage.objects.filter(
                user__email=email,
                start_time__gte=start_date,
                end_time__lte=end_date + timedelta(days=1),
                ).values('software_process__name', 'software_process__icon', 'software_process__os_type','software_process__display_name').annotate(usage_count=Sum('total_usage')))

            self.response_format['data'] = usages_count
            self.response_format['status'] = True
            return Response(self.response_format, status=status.HTTP_200_OK)

        self.response_format['status'] = False
        self.response_format['error'] = 'email required'
        return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)


class getSoftwareDetails(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        self.response_format = ResponseFormat().response
        super().__init__(**kwargs)

    def post(self, request, *args, **kwargs):

        serialzer = GetSoftwareDetailsSerializer(data=request.data)

        if serialzer.is_valid():
            email = serialzer.validated_data.get('email')
            start_date = serialzer.validated_data.get('start_date')
            end_date = serialzer.validated_data.get('end_date')
            display_name = serialzer.validated_data.get('display_name')
            os_type = serialzer.validated_data.get('os_type')

            usages_details = (UserSoftwareUsage.objects.filter(
                user__email=email,
                start_time__gte=start_date,
                end_time__lte=end_date + timedelta(days=1),
                software_process__display_name=display_name,
                software_process__os_type=os_type
            ).values('start_time', 'end_time', 'total_usage'))

            self.response_format['data'] = usages_details
            self.response_format['status'] = True
            return Response(self.response_format, status=status.HTTP_200_OK)

        self.response_format['status'] = False
        self.response_format['error'] = serialzer.errors
        return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)
