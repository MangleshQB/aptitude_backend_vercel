from django.db.models import OuterRef, Exists
from datetime import datetime , date
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import filters, status
from app.models import CustomUser
from app.serializers import CustomUserSerializer
from tracking.models import UserScreenshots
from utils.common import ResponseFormat, get_all_reporting_users


class CustomUserPagination(PageNumberPagination):
    page_size = 10  # Default page size
    page_size_query_param = 'page_size'
    max_page_size = 100


# def get_all_reporting_users(user, flag=False):
    # if flag:
    #     direct_reports = CustomUser.objects.filter(
    #             Exists(UserScreenshots.objects.filter(user=OuterRef('pk'), created_at__date=date.today())))
    # else:
    #     direct_reports = CustomUser.objects.all().exclude(
    #             Exists(UserScreenshots.objects.filter(user=OuterRef('pk'), created_at__date=date.today())))
    # all_reporting_users = set(direct_reports)
    # for report in direct_reports:
    #     all_reporting_users.update(get_all_reporting_users(user=report, flag=flag))
    #
    # return all_reporting_users
    # direct_reports = CustomUser.objects.filter(reporting_to=user)
    # all_reporting_users = set(direct_reports)
    # for report in direct_reports:
    #     all_reporting_users.update(get_all_reporting_users(report))
    #
    # return list(all_reporting_users)


class UserReporting(ModelViewSet):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()
    pagination_class = CustomUserPagination

    def list(self, request, *args, **kwargs):

        today = date.today()
        mode = request.GET.get('mode', '')
        reporting = request.GET.get('reporting')


        if mode == 'all':
            all_user_queryset = CustomUser.objects.all()
            paginated_queryset = self.paginate_queryset(all_user_queryset)
            all_users_serializer = self.get_serializer(paginated_queryset, many=True)
            return self.get_paginated_response(all_users_serializer.data)

        queryset = self.filter_queryset(self.get_queryset())
        user_permissions = request.user.groups.first().permissions.filter(
            content_type__model='customuser'
        ).values_list('codename', flat=True)
        base_permissions = [permission.split('_')[0] for permission in user_permissions]

        if 'all' in base_permissions:

            if reporting == 'true':
                all_user_queryset = CustomUser.objects.filter(
                Exists(UserScreenshots.objects.filter(user=OuterRef('pk'), created_at__date=today))
            )
            else:
                all_user_queryset = CustomUser.objects.exclude(
                Exists(UserScreenshots.objects.filter(user=OuterRef('pk'), created_at__date=today))
            )

            paginated_queryset = self.paginate_queryset(all_user_queryset)
            all_users_serializer = self.get_serializer(paginated_queryset, many=True)

            active_count = CustomUser.objects.filter(
                Exists(UserScreenshots.objects.filter(user=OuterRef('pk'), created_at__date=today))
            ).count()
            inactive_count = CustomUser.objects.exclude(
                Exists(UserScreenshots.objects.filter(user=OuterRef('pk'), created_at__date=today))
            ).count()

            response_data = {
                'users': all_users_serializer.data,
                'active_count': active_count if active_count else 0,
                'inactive_count': inactive_count if inactive_count else 0,
            }
            return self.get_paginated_response(response_data)


        elif 'team' in base_permissions:

            team_user_queryset_email = [i.email for i in get_all_reporting_users(request.user)]
            team_user_queryset = CustomUser.objects.filter(email__in=team_user_queryset_email)

            if reporting == 'true':

                team_user_queryset_data = team_user_queryset.filter(
                Exists(UserScreenshots.objects.filter(user=OuterRef('pk'), created_at__date=today)))

                paginated_queryset = self.paginate_queryset(team_user_queryset_data)
                team_users_serializer = self.get_serializer(paginated_queryset, many=True)

                active_count = team_user_queryset_data.count()
                inactive_count = team_user_queryset.count() - team_user_queryset_data.count()

                response_data = {
                    'users': team_users_serializer.data,
                    'active_count': active_count if active_count else 0,
                    'inactive_count': inactive_count if inactive_count else 0,
                }
                return self.get_paginated_response(response_data)

            else:

                team_user_queryset_data = team_user_queryset.exclude(
                Exists(UserScreenshots.objects.filter(user=OuterRef('pk'), created_at__date=today)))

                paginated_queryset = self.paginate_queryset(team_user_queryset_data)
                team_users_serializer = self.get_serializer(paginated_queryset, many=True)


                inactive_count = team_user_queryset_data.count()
                active_count = team_user_queryset.count() - team_user_queryset_data.count()

                response_data = {
                    'users': team_users_serializer.data,
                    'active_count': active_count if active_count else 0,
                    'inactive_count': inactive_count if inactive_count else 0,
                }
                return self.get_paginated_response(response_data)


        elif 'owned' in base_permissions:

            is_active_user = UserScreenshots.objects.filter(user=request.user, created_at__date=today)

            if reporting == 'true':

                if is_active_user.exists():
                     owned_user_queryset = CustomUser.objects.filter(id=request.user.id)
                else:
                    owned_user_queryset = CustomUser.objects.none()

            else:

                if not is_active_user.exists():
                    owned_user_queryset = CustomUser.objects.filter(id=request.user.id)
                else:
                    owned_user_queryset = CustomUser.objects.none()

            # Apply pagination only to users
            paginated_queryset = self.paginate_queryset(owned_user_queryset)
            owned_user_serializer = self.get_serializer(paginated_queryset, many=True)

            # Determine active/inactive counts

            response_data = {
                'users': owned_user_serializer.data,  # Paginated users
                'active_count': 1 if is_active_user.exists() else 0,
                'inactive_count': 1 if not is_active_user.exists() else 0,
            }

            # Return response with pagination metadata for users
            paginated_response = self.get_paginated_response(response_data['users'])
            paginated_response.data.update({
                'active_count': response_data['active_count'],
                'inactive_count': response_data['inactive_count']
            })
            return paginated_response


        # For other cases
        paginated_queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(paginated_queryset, many=True)
        return self.get_paginated_response(serializer.data)



