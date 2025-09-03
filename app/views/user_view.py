from operator import attrgetter

from django.db.models import Q
from rest_framework import status, views, permissions, serializers, filters
from rest_framework.views import APIView
from itertools import chain
from app.management.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from app.models import CustomUser
from app.serializers import CustomUserSerializer, CustomUserWithHoursSerializer
from utils.Qbkafka import QbKafkaProducer
from utils.common import ResponseFormat, get_all_reporting_users
from rest_framework.pagination import PageNumberPagination

class Pagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


try:
    qb_kafka = QbKafkaProducer()
except:
    pass


# def get_all_reporting_users_filter(user, req_user=True, is_screenshot_active=None, search_term=None, search_filter=None):
#
#     if is_screenshot_active is not None and search_term:
#         direct_reports = CustomUser.objects.filter(reporting_to=user, is_screenshot_active=is_screenshot_active).filter(search_filter)
#     elif is_screenshot_active is not None:
#         direct_reports = CustomUser.objects.filter(reporting_to=user, is_screenshot_active=is_screenshot_active)
#     else:
#         direct_reports = CustomUser.objects.filter(reporting_to=user)
#
#     all_reporting_users = direct_reports
#     if user not in all_reporting_users and req_user:
#         if is_screenshot_active is not None and search_term:
#             if user.is_screenshot_active == is_screenshot_active and (
#                 search_term.lower() in user.email.lower() or
#                 search_term.lower() in user.username.lower() or
#                 search_term.lower() in user.first_name.lower() or
#                 search_term.lower() in user.last_name.lower() or
#                 search_term.lower() in user.phone_number.lower()
#             ):
#                 all_reporting_users |= user
#
#         elif is_screenshot_active is not None:
#             if user.is_screenshot_active == is_screenshot_active:
#                 all_reporting_users |= user
#         elif search_term:
#             email_check = search_term.lower() in user.email.lower() if user.email else False
#             username_check = search_term.lower() in user.username.lower() if user.username else False
#             first_name_check = search_term.lower() in user.first_name.lower() if user.first_name else False
#             last_name_check = search_term.lower() in user.last_name.lower() if user.last_name else False
#             phone_number_check = search_term.lower() in user.phone_number.lower() if user.phone_number else False
#
#             if email_check or username_check or first_name_check or last_name_check or phone_number_check:
#                 all_reporting_users |= user
#         else:
#             all_reporting_users |= user
#
#     for report in direct_reports:
#         subordinates = get_all_reporting_users_filter(report, req_user=False, is_screenshot_active=is_screenshot_active,
#                                        search_term=search_term, search_filter=search_filter)
#         if len(subordinates) > 0:
#             all_reporting_users |= subordinates
#
#     return all_reporting_users


# def get_all_reporting_users_filter(user, req_user=True):
#     def fetch_reporting_emails(user):
#         # Use values_list to fetch only emails of direct reports
#         return CustomUser.objects.filter(reporting_to=user).values_list('email', flat=True)
#
#     all_emails = set(fetch_reporting_emails(user))  # Get direct reports' emails
#     if req_user:
#         all_emails.add(user.email)  # Add the requesting user's email if needed
#
#     for report_email in list(all_emails):  # Iterate over collected emails
#         reporting_user = CustomUser.objects.get(email=report_email)  # Retrieve user object
#         all_emails.update(fetch_reporting_emails(reporting_user))  # Add their direct reports' emails
#
#     return list(all_emails)



from utils.views import CustomModelViewSet

class UserView(CustomModelViewSet):
    queryset = CustomUser.objects.all().exclude(email='admin@gmail.com')
    permission_classes = [IsAuthenticated]

    serializer_class = CustomUserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'phone_number', 'last_name', 'first_name']

    pagination_class = Pagination

    def __init__(self, **kwargs):
        self.response_format = ResponseFormat().response
        super().__init__(**kwargs)

    def get_serializer_class(self):
        if self.action == 'list' and self.request.GET.get('calculate_hours', '').lower() == 'true':
            return CustomUserWithHoursSerializer
        return super().get_serializer_class()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['start_date'] = self.request.GET.get('start_date', None)
        context['end_date'] = self.request.GET.get('end_date', None)
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'user':request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        self.response_format["data"] = serializer.data
        self.response_format["status"] = True
        return Response(self.response_format, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        activity_status = request.GET.get('is_screenshot_active', '')
        mode = request.GET.get('mode', '')
        search_term = request.GET.get('search', '')

        user = request.user.groups.first().permissions.filter(content_type__model='customuser').values_list('codename',flat=True)
        base_permissions = [permission.split('_')[0] for permission in user]

        search_filter = Q()
        if search_term:
            search_filter |= Q(username__icontains=search_term) | Q(phone_number__icontains=search_term) | Q(
                last_name__icontains=search_term) | Q(first_name__icontains=search_term) | Q(
                email__icontains=search_term)

        print('search_filter', search_filter)

        if mode == 'all':
            all_user_queryset = CustomUser.objects.filter(search_filter).exclude(email='admin@gmail.com')
            page = self.paginate_queryset(all_user_queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            all_users_serializer = self.get_serializer(all_user_queryset, many=True)
            self.response_format['status'] = True
            self.response_format['data'] = all_users_serializer.data
            return Response(self.response_format, status=status.HTTP_200_OK)

        # General queryset filtering
        queryset = self.filter_queryset(self.get_queryset()).filter(search_filter)

        # Handling based on permissions
        if 'all' in base_permissions:
            if activity_status == 'true':
                all_user_queryset = CustomUser.objects.filter(is_screenshot_active=True).filter(search_filter).exclude(
                    email='admin@gmail.com')
            elif activity_status == 'false':
                all_user_queryset = CustomUser.objects.filter(is_screenshot_active=False).filter(search_filter).exclude(
                    email='admin@gmail.com')
            else:
                all_user_queryset = CustomUser.objects.filter(search_filter).exclude(email='admin@gmail.com')

            page = self.paginate_queryset(all_user_queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            all_users_serializer = self.get_serializer(all_user_queryset, many=True)
            self.response_format['status'] = True
            self.response_format['data'] = all_users_serializer.data
            return Response(self.response_format, status=status.HTTP_200_OK)

        elif 'team' in base_permissions:
            own_user_queryset = None

            team_user_queryset_email =[i.email for i in  get_all_reporting_users(request.user)]

            # team_user_queryset = get_all_reporting_users_filter(user=request.user)
            if not team_user_queryset_email:
                self.response_format['status'] = False
                self.response_format['data'] = ''
                self.response_format['message'] = 'No User Found'

                return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)


            if activity_status == 'true':
                team_user_queryset = CustomUser.objects.filter(email__in=team_user_queryset_email, is_screenshot_active=True)
                if search_term:
                    team_user_queryset = team_user_queryset.filter(search_filter)
            elif activity_status == 'false':
                team_user_queryset = CustomUser.objects.filter(email__in=team_user_queryset_email, is_screenshot_active=False)
                if search_term:
                    team_user_queryset = team_user_queryset.filter(search_filter)
            else:
                team_user_queryset = CustomUser.objects.filter(email__in=team_user_queryset_email)
                if search_term:
                    team_user_queryset = team_user_queryset.filter(search_filter)

            page = self.paginate_queryset(team_user_queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            team_users_serializer = self.get_serializer(team_user_queryset, many=True)
            self.response_format['status'] = True
            self.response_format['data'] = team_users_serializer.data
            return Response(self.response_format, status=status.HTTP_200_OK)

        elif 'owned' in base_permissions:
            if activity_status == 'true':
                owned_user_queryset = CustomUser.objects.filter(id=request.user.id, is_screenshot_active=True).filter(
                    search_filter)
            elif activity_status == 'false':
                owned_user_queryset = CustomUser.objects.filter(id=request.user.id,
                                                                is_screenshot_active=False).filter(search_filter)
            else:
                owned_user_queryset = CustomUser.objects.filter(id=request.user.id).filter(search_filter)

            page = self.paginate_queryset(owned_user_queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            owned_user_serializer = self.get_serializer(owned_user_queryset, many=True)
            self.response_format['status'] = True
            self.response_format['data'] = owned_user_serializer.data
            return Response(self.response_format, status=status.HTTP_200_OK)

        # Default pagination if no specific permission handling
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

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        is_surveillance_changed = True if 'is_surveillance_active' in request.data and request.data['is_surveillance_active'] != instance.is_surveillance_active else False
        self.perform_update(serializer)

        if is_surveillance_changed:
            qb_kafka.publish(
                'User is_surveillance_active update.',
                {
                    'email': instance.email,
                    'is_surveillance_active': instance.is_surveillance_active
                }
            )
        else:
            pass

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        self.response_format['status'] = True
        self.response_format['data'] = serializer.data

        self.response_format['message'] = 'User Updated Successfully'
        return Response(self.response_format, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):

        user = request.user.groups.first().permissions.filter(content_type__model='customuser').values_list('codename',
                                                                                                            flat=True)
        base_permissions = [permission.split('_')[0] for permission in user]

        if 'all' in base_permissions:
            instance = self.get_object()
            self.perform_destroy(instance)
            self.response_format['status'] = True
            self.response_format['message'] = 'User Deleted Successfully'
            return Response(self.response_format, status=status.HTTP_200_OK)
        
        self.response_format['status'] = False
        self.response_format['message'] = 'User have not permission to perform this action'
        return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)


class ActivateAllUsers(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        self.response_format = ResponseFormat().response
        super().__init__(**kwargs)

    def get(self, request):
        users = CustomUser.objects.filter(is_active=True).update(is_surveillance_active=True)
        self.response_format['status'] = True
        self.response_format['message'] = "Users have been updated successfully."
        return Response(self.response_format, status=status.HTTP_200_OK)
