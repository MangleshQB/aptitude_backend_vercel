from rest_framework.permissions import IsAuthenticated
from app.models import CustomUser
from hrms.models import Leave
from hrms.serializer import LeaveSerializer
from utils.common import get_all_reporting_users
from utils.views import CustomModelViewSet
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

class LeaveViewSet(CustomModelViewSet):
    queryset = Leave.objects.filter(is_deleted=False).order_by('-id')
    serializer_class = LeaveSerializer
    permission_classes = [IsAuthenticated]

    search_fields = [
        'user',
        'leave_type',
        'date',
        'reporting_status',
        'reporting_approve_by',
        'reporting_approve_time',
        'status',
        'approve_by',
        'approve_time',
        'description',
    ]

    ordering_fields = [
        'user',
        'leave_type',
        'date',
        'reporting_status',
        'reporting_approve_by',
        'reporting_approve_time',
        'status',
        'approve_by',
        'approve_time',
        'description',
    ]


    def list(self, request, *args, **kwargs):

        permissions = request.user.groups.all().first().permissions.filter(
            content_type__model='leave').values_list('codename', flat=True)

        # print(permissions)
        base_permissions = [permission.split('_')[0] for permission in permissions]

        # code = 'hrms.owned_leave'
        #
        # user_permission = request.user.get_group_permissions()
        # print('user_permission------------->',code in user_permission)
        #
        # print('CHeck test = ', request.user.has_perm(code))
        #
        # if request.user.has_perm(code):
        #     print('Has Permission')
        # else:
        #     print('Has not Permission', request.user.has_perm(code))

        if 'all' in base_permissions:
            self.queryset = Leave.objects.filter(is_deleted=False).order_by('-id')
        elif 'team' in base_permissions:
            # team_user_queryset = request.user.subordinates.all()
            reporting_user = get_all_reporting_users(request.user)
            self.queryset = Leave.objects.filter(user__in=reporting_user, is_deleted=False).order_by('-id')
        elif 'owned' in base_permissions:
            self.queryset = Leave.objects.filter(user=request.user, is_deleted=False).order_by('-id')
        else:
            self.response_format["status"] = False
            self.response_format["message"] = "User does not have permission."
            return Response(self.response_format, status=HTTP_400_BAD_REQUEST)


        if request.GET.get("search", None) or request.GET.get("ordering", None):
            queryset = self.filter_queryset(self.get_queryset())
        else:
            queryset = self.get_queryset()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        self.response_format["data"] = serializer.data
        self.response_format["status"] = True
        if not serializer.data:
            self.response_format["message"] = "No data found!"
        return Response(self.response_format, status=HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        permissions = request.user.groups.all().first().permissions.filter(
            content_type__model='leave').values_list('codename', flat=True)

        base_permissions = [permission.split('_')[0] for permission in permissions]
        obj = self.get_object()

        if 'all' in base_permissions:
            self.queryset = Leave.objects.filter(is_deleted=False).order_by('-id')
        elif 'team' in base_permissions:
            # team_user_queryset = request.user.subordinates.all()
            team_user_queryset = get_all_reporting_users(request.user)
            # reporting_user = [i.email for i in reporting_user]
            if obj not in Leave.objects.filter(user__in=team_user_queryset, is_deleted=False).order_by('-id'):
                self.response_format["status"] = False
                self.response_format["message"] = "User does not have permission."
                return Response(self.response_format, status=HTTP_400_BAD_REQUEST)
        elif 'owned' in base_permissions:
            if obj not in Leave.objects.filter(user=request.user, is_deleted=False).order_by('-id'):
                self.response_format["status"] = False
                self.response_format["message"] = "User does not have permission."
                return Response(self.response_format, status=HTTP_400_BAD_REQUEST)
        else:
            self.response_format["status"] = False
            self.response_format["message"] = "User does not have permission."
            return Response(self.response_format, status=HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(instance=obj)
        self.response_format["data"] = serializer.data
        self.response_format["status"] = True
        if not serializer.data:
            self.response_format["message"] = "No data found!"
        return Response(self.response_format, status=HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        permissions = request.user.groups.all().first().permissions.filter(
            content_type__model='leave').values_list('codename', flat=True)

        base_permissions = [permission.split('_')[0] for permission in permissions]
        user = request.data.get('user', '')

        if user:
            user = CustomUser.objects.get(id=user)

        if 'all' in base_permissions:
            pass
        elif 'team' in base_permissions:
            # team_user_queryset = request.user.subordinates.all()
            team_user_queryset = get_all_reporting_users(request.user)
            if user not in team_user_queryset:
                self.response_format["status"] = False
                self.response_format["message"] = "User does not have permission."
                return Response(self.response_format, status=HTTP_400_BAD_REQUEST)
        elif 'owned' in base_permissions:
            if user != request.user:
                self.response_format["status"] = False
                self.response_format["message"] = "User does not have permission."
                return Response(self.response_format, status=HTTP_400_BAD_REQUEST)
        else:
            self.response_format["status"] = False
            self.response_format["message"] = "User does not have permission."
            return Response(self.response_format, status=HTTP_400_BAD_REQUEST)



        serializer = self.serializer_class(data=request.data,
                                           context={'created_by': request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        print(serializer.data)
        self.response_format["data"] = serializer.data
        self.response_format["status"] = True
        return Response(self.response_format, status=HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        permissions = request.user.groups.all().first().permissions.filter(
            content_type__model='leave').values_list('codename', flat=True)

        base_permissions = [permission.split('_')[0] for permission in permissions]
        obj = self.get_object()

        if 'all' in base_permissions:
            self.queryset = Leave.objects.filter(is_deleted=False).order_by('-id')
        elif 'team' in base_permissions:

            # team_user_queryset = request.user.subordinates.all()
            team_user_queryset = get_all_reporting_users(request.user)
            if obj not in Leave.objects.filter(user__in=team_user_queryset, is_deleted=False).order_by('-id'):
                self.response_format["status"] = False
                self.response_format["message"] = "User does not have permission."
                return Response(self.response_format, status=HTTP_400_BAD_REQUEST)
        elif 'owned' in base_permissions:
            if obj not in Leave.objects.filter(user=request.user, is_deleted=False).order_by('-id'):
                self.response_format["status"] = False
                self.response_format["message"] = "User does not have permission."
                return Response(self.response_format, status=HTTP_400_BAD_REQUEST)
        else:
            self.response_format["status"] = False
            self.response_format["message"] = "User does not have permission."
            return Response(self.response_format, status=HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(instance=obj, data=request.data, context={'updated_by': request.user, 'base_permissions':base_permissions},
                                           partial=True)

        if serializer.is_valid():
            serializer.save()
            self.response_format["data"] = serializer.data
            self.response_format["status"] = True
            return Response(self.response_format, status=HTTP_200_OK)
        else:
            self.response_format["data"] = serializer.errors
            self.response_format["status"] = False
            self.response_format["error"] = HTTP_400_BAD_REQUEST
            self.response_format["message"] = "Validation failed"
            return Response(self.response_format, status=HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        permissions = request.user.groups.all().first().permissions.filter(
            content_type__model='leave').values_list('codename', flat=True)

        base_permissions = [permission.split('_')[0] for permission in permissions]
        obj = self.get_object()

        if 'all' in base_permissions:
            self.queryset = Leave.objects.filter(is_deleted=False).order_by('-id')
        elif 'team' in base_permissions:
            team_user_queryset = get_all_reporting_users(request.user)
            if obj not in Leave.objects.filter(user__in=team_user_queryset, is_deleted=False).order_by('-id'):
                self.response_format["status"] = False
                self.response_format["message"] = "User does not have permission."
                return Response(self.response_format, status=HTTP_400_BAD_REQUEST)
        elif 'owned' in base_permissions:
            if obj not in Leave.objects.filter(user=request.user, is_deleted=False).order_by('-id'):
                self.response_format["status"] = False
                self.response_format["message"] = "User does not have permission."
                return Response(self.response_format, status=HTTP_400_BAD_REQUEST)
        else:
            self.response_format["status"] = False
            self.response_format["message"] = "User does not have permission."
            return Response(self.response_format, status=HTTP_400_BAD_REQUEST)

        try:
            obj.soft_delete()
            return Response(self.response_format, status=HTTP_200_OK)
        except Exception as e:
            print('Error = ', e)
            self.response_format["status"] = False
            self.response_format["error"] = HTTP_400_BAD_REQUEST
            self.response_format["message"] = "Deletion failed"
            return Response(self.response_format, status=HTTP_400_BAD_REQUEST)
