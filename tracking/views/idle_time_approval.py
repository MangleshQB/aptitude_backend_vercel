from decimal import Decimal
from datetime import datetime, timedelta
from django.db.models.fields import IntegerField
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Case, When, Value
from app.models import CustomUser
from tracking.models import IdleTimeApproval, IdleTimeApprovalReason, UserMouseTracking
from tracking.serializer import IdleTimeApprovalSerializer, IdleTimeApprovalReasonSerializer, IdleTimeRequestMultipleSerializer
from utils.common import get_all_reporting_users
from utils.views import CustomModelViewSet


class IdleTimeApprovalReasonList(CustomModelViewSet):

    queryset = IdleTimeApprovalReason.objects.filter(is_deleted=False).order_by('-id')
    serializer_class = IdleTimeApprovalReasonSerializer
    permission_classes = [IsAuthenticated]

def time_to_minutes(time_string):
        hours, minutes, seconds = map(int, time_string.split(':'))
        total_minutes = float(hours * 60) + float(minutes) + float(seconds / 60)
        return total_minutes

class IdleTimeApprovalViewSet(CustomModelViewSet):
    queryset = IdleTimeApproval.objects.filter(is_deleted=False).order_by('-id')
    serializer_class = IdleTimeApprovalSerializer
    permission_classes = [IsAuthenticated]

    search_fields = [
        'user__first_name',
        'user__last_name',
        'description',
        'status',
        'reason__name',
        'idle_time',
        'approved_time',
        'idle_start_time',
        'idle_end_time'
    ]

    ordering_field = [
        'description',
        'status',
        'reason__name',
        'idle_time',
        'approved_time',
        'approved_by__first_name',
    ]

    def list(self, request, *args, **kwargs):

        permissions = request.user.groups.all().first().permissions.filter(
            content_type__model='customuser').values_list('codename', flat=True)

        base_permissions = [permission.split('_')[0] for permission in permissions]

        if 'all' in base_permissions:
            # self.queryset = IdleTimeApproval.objects.filter(is_deleted=False).order_by('-status')
            self.queryset = IdleTimeApproval.objects.filter(is_deleted=False)
        elif 'team' in base_permissions:
            reporting_user = get_all_reporting_users(request.user)
            # self.queryset = IdleTimeApproval.objects.filter(user__in=reporting_user, is_deleted=False).order_by('-status')
            self.queryset = IdleTimeApproval.objects.filter(user__in=reporting_user, is_deleted=False)
        elif 'owned' in base_permissions:
            # self.queryset = IdleTimeApproval.objects.filter(user=request.user, is_deleted=False).order_by('-status')
            self.queryset = IdleTimeApproval.objects.filter(user=request.user, is_deleted=False)
        else:
            self.response_format["status"] = False
            self.response_format["message"] = "User does not have permission."
            return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)

        start_date = request.GET.get("start_date", None)
        end_date = request.GET.get("end_date", None)

        if start_date and end_date:
            date_range = [(datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=i))
                          for i in range((datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")).days + 1)]
            self.queryset = self.queryset.filter(idle_end_time__date__in=date_range).annotate(
                status_order=Case(
                    When(status='pending', then=Value(1)),
                    When(status='rejected', then=Value(2)),
                    When(status='approved', then=Value(3)),
                    output_field=IntegerField(),
                )
            ).order_by('status_order', 'status', '-id')
        else:
            month = datetime.now().month
            year = datetime.now().year

            self.queryset = self.queryset.filter(idle_end_time__date__month=month,idle_end_time__date__year=year).annotate(
                status_order=Case(
                    When(status='pending', then=Value(1)),
                    When(status='rejected', then=Value(2)),
                    When(status='approved', then=Value(3)),
                    output_field=IntegerField(),
                )
            ).order_by('status_order', 'status', '-id')


        if request.GET.get("search", None) or request.GET.get("ordering", None):

            queryset = self.filter_queryset(self.get_queryset())
        else:
            queryset = self.get_queryset()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True, context={'user':request.user})
        self.response_format["data"] = serializer.data
        self.response_format["status"] = True
        if not serializer.data:
            self.response_format["message"] = "No data found!"
        return Response(self.response_format, status=status.HTTP_200_OK)


    def create(self, request, *args, **kwargs):

        user = CustomUser.objects.filter(email=request.data['user']).first()
        ref_idle_time = request.data.get('ref_idle_time', None)
        mouse_tracking_obj = UserMouseTracking.objects.filter(id=ref_idle_time).first()


        idle_time = request.data.get('idle_time', None)
        if idle_time:
            idle_time = time_to_minutes(idle_time)
            request.data['idle_time'] = round(Decimal(idle_time),2)


        if idle_time:
            idle_time = float(idle_time)

            if mouse_tracking_obj:
                total_time = float(mouse_tracking_obj.idle_time)
                total_approval_time = IdleTimeApproval.objects.filter(ref_idle_time__id=ref_idle_time, status__in=[IdleTimeApproval.approved, IdleTimeApproval.pending]).aggregate(total_approved_time=Sum('idle_time'))
                if total_approval_time['total_approved_time']:
                    total_approval_time = total_approval_time['total_approved_time']
                    if total_time <= float(total_approval_time) + idle_time:
                        self.response_format["status"] = False
                        self.response_format["message"] = "your approval time is bigger than total idle time of this data"
                        return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)


        if mouse_tracking_obj and float(mouse_tracking_obj.idle_time) <= 5.0:
            request.data['status'] = IdleTimeApproval.approved
            request.data['approved_by'] = request.user.id


        if not user:
            self.response_format["status"] = False
            self.response_format["message"] = "Email is wrong"
            return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)

        request.data['user'] = user.id

        serializer = self.serializer_class(data=request.data,
                                           context={'created_by': request.user, 'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        self.response_format["data"] = serializer.data
        self.response_format["status"] = True
        return Response(self.response_format, status=status.HTTP_200_OK)


    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj == request.user:
            if request.data['status'] != obj.status:
                self.response_format["status"] = False
                self.response_format["error"] = status.HTTP_400_BAD_REQUEST
                self.response_format["message"] = "You have not permission for owned status changed"
                return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)

        if request.data.get('status', None) == IdleTimeApproval.approved and request.data.get('status', None) != obj.status:
            request.data['approved_by'] = request.user.id
            request.data['approved_time'] = str(datetime.now())


        serializer = self.serializer_class(instance=obj, data=request.data, context={'updated_by': request.user, 'request': request},
                                           partial=True)
        if serializer.is_valid():
            serializer.save()
            self.response_format["data"] = serializer.data
            self.response_format["status"] = True
            return Response(self.response_format, status=status.HTTP_200_OK)
        else:
            self.response_format["data"] = serializer.errors
            self.response_format["status"] = False
            self.response_format["error"] = status.HTTP_400_BAD_REQUEST
            self.response_format["message"] = "Validation failed"
            return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(
        method="post",
        request_body=IdleTimeRequestMultipleSerializer,
        # responses=serializer_class(many=True)
    )
    @action(detail=False, methods=["POST"], name="Create Multiple")
    def create_multiple(self, request, *args, **kwargs):
        serializer = IdleTimeRequestMultipleSerializer(data=request.data, context={'created_by': request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        self.response_format["data"] = 'Multiple request is successful'
        self.response_format["status"] = True
        return Response(self.response_format, status=status.HTTP_200_OK)
