from datetime import datetime, timedelta
from django.contrib.auth.models import Permission
from rest_framework import status, permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import CustomUser
from tracking.models import UserScreenshots, UserMouseTracking
from tracking.serializer import UserMouseTrackingSerializer
from utils.common import ResponseFormat, get_all_reporting_users
from rest_framework.filters import SearchFilter


class UserMouseTrackingView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = UserMouseTrackingSerializer

    filter_backends = [SearchFilter]
    search_fields = ["email", "created_at"]

    def __init__(self, **kwargs):
        self.response_format = ResponseFormat().response
        super().__init__(**kwargs)

    def post(self, request, *args, **kwargs):

        serializer = UserMouseTrackingSerializer(data=request.data, context={'user': request.user, 'created_by':request.user})

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            self.response_format['data'] = serializer.data
            self.response_format['status'] = True
            return Response(self.response_format, status=status.HTTP_201_CREATED)

        self.response_format['error'] = serializer.errors
        self.response_format['status'] = False
        return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)


class UserMouseTrackingGETView(APIView):
    permission_classes = [IsAuthenticated]
    # authentication_classes = [TokenAuthentication]
    serializer_class = UserMouseTrackingSerializer
    # permission_classes = [CheckUser]

    search_fields = ["email", "created_at"]

    def __init__(self, **kwargs):
        self.response_format = ResponseFormat().response
        super().__init__(**kwargs)

    def get(self, request, *args, **kwargs):
        email = request.GET.get('email', '')
        # date = request.GET.get('date', '')
        start_date = request.GET.get('start_date', '')
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 25))
        if start_date:
            start_date = datetime.strptime(start_date, "%d/%m/%Y").date()
        end_date = request.GET.get('end_date', '')
        if end_date:
            end_date = datetime.strptime(end_date, "%d/%m/%Y").date()
        permissions = request.user.groups.all().first().permissions.filter(content_type__model='usermousetracking').values_list('codename', flat=True)
        base_permissions = [permission.split('_')[0] for permission in permissions]

        is_email_accessible = False
        mouse_track = None

        if email:
            email_user = CustomUser.objects.filter(email=email).first()

            first_name = email_user.first_name
            last_name = email_user.last_name

            self.response_format['user'] = {'first_name': first_name, 'last_name': last_name}
            if 'all' in base_permissions:
                if start_date and end_date:
                    mouse_track = UserMouseTracking.objects.filter(user__email=email, idle_start_time__date__range=[start_date, end_date+timedelta(days=1)])
                else:
                    mouse_track = UserMouseTracking.objects.filter(user__email=email,
                                                                   idle_start_time__date=datetime.now().date())
                is_email_accessible = True

            if 'team' in base_permissions:
                reporting_user = get_all_reporting_users(request.user)
                reporting_user = [i.email for i in reporting_user]

                if email in reporting_user:
                    if start_date and end_date:
                        mouse_track = UserMouseTracking.objects.filter(user__email=email, idle_start_time__date__range=[start_date, end_date+timedelta(days=1)])
                    else:
                        mouse_track = UserMouseTracking.objects.filter(user__email=email,
                                                                       idle_start_time__date=datetime.now().date())
                    is_email_accessible = True

            if 'owned' in base_permissions:
                if request.user.email == email:
                    if start_date and end_date:
                        mouse_track = UserMouseTracking.objects.filter(user__email=email, idle_start_time__date__range=[start_date, end_date+timedelta(days=1)])
                    else:
                        mouse_track = UserMouseTracking.objects.filter(user__email=email,
                                                                       idle_start_time__date=datetime.now().date())
                    is_email_accessible = True

            if mouse_track or is_email_accessible:
                total_items = mouse_track.count()
                start_index = (page - 1) * page_size
                end_index = start_index + page_size
                paginated_mouse_track = mouse_track[start_index:end_index]

                serializer = self.serializer_class(paginated_mouse_track, many=True)

                self.response_format['data'] = {
                    'count': total_items,
                    'page': page,
                    'page_size': page_size,
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
