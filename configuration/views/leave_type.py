from django.db.models import F
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from configuration.models import LeaveTypes, LeaveBalance
from configuration.serializers import LeaveTypesSerializer
from utils.views import CustomModelViewSet
from rest_framework import status


class LeaveTypeViewSet(CustomModelViewSet):
    permission_classes = [IsAuthenticated]

    queryset = LeaveTypes.objects.filter(is_deleted=False).order_by('-id')
    serializer_class = LeaveTypesSerializer

    search_fields = [
        'type',
        'limit',
        'start_range',
        'end_range',
        'el_after',
        'lc_before',
        'wfh_start_time',
        'wfh_end_time',
        'fh_hours',
        'sh_hours',
    ]

    ordering_fields = [
        'type',
        'limit',
        'start_range',
        'end_range',
        'el_after',
        'lc_before',
        'wfh_start_time',
        'wfh_end_time',
        'fh_hours',
        'sh_hours',
    ]

    def list(self, request, *args, **kwargs):

        email = request.GET.get('email', None)
        if email:
            user_leave_type = []
            no_balance_list = list(LeaveTypes.objects.filter(is_balance=False).annotate(type_id=F('id')).values('type_id', 'type'))

            leave_balance = list(LeaveBalance.objects.filter(user__email=email,balance__gt=0).annotate(type_id=F('leave_type__id'),type=F('leave_type__type')).values('type_id','type'))

            user_leave_type.extend(no_balance_list)
            user_leave_type.extend(leave_balance)

            self.response_format["data"] = user_leave_type
            self.response_format["status"] = True

            return Response(self.response_format, status=status.HTTP_200_OK)


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
        return Response(self.response_format, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        type = request.data.get('type', None)
        permissions = request.user.groups.all().first().permissions.filter(
            content_type__model='customuser').values_list('codename', flat=True)

        base_permissions = [permission.split('_')[0] for permission in permissions]
        # print(base_permissions)
        if not 'all' in base_permissions:
            self.response_format["status"] = False
            self.response_format["message"] = "User does not have permission."
            return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)

        if not type:
            self.response_format["status"] = False
            self.response_format["message"] = "type is required"
            return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)
        leave_type, created= LeaveTypes.objects.get_or_create(type=type)
        # print(leave_type.id)
        # print(created)
        serializer = self.serializer_class(instance=leave_type, data=request.data,context={'created_by': request.user} if created else {'updated_by': request.user})

        serializer.is_valid(raise_exception=True)
        serializer.save()
        self.response_format["data"] = serializer.data
        self.response_format["status"] = True
        return Response(self.response_format, status=status.HTTP_200_OK)

