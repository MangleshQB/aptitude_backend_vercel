from django.db.models import Sum
from rest_framework import serializers
from django.db import transaction
import copy
from app.models import CustomUser
from decimal import Decimal
from app.serializers import CustomUserSerializer
from tracking.models import UserMouseTracking, UserScreenshots, UserSoftwareUsage, IdleTimeApproval, \
    IdleTimeApprovalReason ,APIErrorLogs
from configuration.models import SoftwareProcess
from utils.serializer import BaseModelSerializerCore, RelatedFieldAlternative
from rest_framework.exceptions import ValidationError

class UserMouseTrackingSerializer(BaseModelSerializerCore):
    idle_time_approval_details = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserMouseTracking
        fields = ['id','idle_time', 'idle_start_time', 'idle_end_time', 'created_at', 'updated_at', 'idle_time_approval_details']

    def create(self, validated_data):
        user = self.context['user']
        instance = UserMouseTracking.objects.create(**validated_data, user=user)
        return instance

    def get_idle_time_approval_details(self, obj):
        idle_data = IdleTimeApproval.objects.filter(ref_idle_time=obj).values()
        if idle_data:
            idle_data = self.format_seconds_to_hms(idle_data)
        else:
            idle_data = []

        return idle_data

    @staticmethod
    def format_seconds_to_hms(idle_data):
        final_idle_data = []
        for i in idle_data:
            try:
                temp_dict = copy.deepcopy(i)
                total_seconds = temp_dict['idle_time'] * 60
                hours = int(total_seconds // 3600)
                minutes = int((total_seconds % 3600) // 60)
                seconds = int(total_seconds % 60)

                temp_dict['idle_time'] = f"{hours:02}:{minutes:02}:{seconds:02}"
                final_idle_data.append(temp_dict)
            except:
                continue
        return final_idle_data

class UserScreenshotCountSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class UserScreenshotSerializer(serializers.ModelSerializer):
    # screenshots = serializers.FileField()
    class Meta:
        model = UserScreenshots
        fields = ['file', 'created_at', 'user']


class ScreenshotsSerializer(BaseModelSerializerCore):
    class Meta:
        model = UserScreenshots
        fields = ['file']
        # read_only = ['user']

    def create(self, validated_data):
        user = self.context['user']
        return UserScreenshots.objects.create(**validated_data, user=user)


class UserSoftwareUsageSerializer(serializers.ModelSerializer):
    name = serializers.CharField(write_only=True)
    os = serializers.CharField(write_only=True)

    class Meta:
        model = UserSoftwareUsage
        fields = [
            'start_time',
            'end_time',
            'total_usage',
            'name',
            'os'
        ]

    @transaction.atomic
    def create(self, validated_data):
        name = validated_data.pop('name')
        os = validated_data.pop('os')
        software_process = SoftwareProcess.objects.filter(name__icontains=name).first()

        if software_process is None:
            software_process = SoftwareProcess.objects.create(name=name, display_name=name, os_type=os)

        user_software_usage = UserSoftwareUsage.objects.create(**validated_data, user=self.context['user'],
                                                               software_process=software_process)

        return user_software_usage


class GetUserSoftwareUsageSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    email = serializers.EmailField()

    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError("The start_date must be earlier than the end_date.")

        return data


class GetSoftwareDetailsSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    email = serializers.EmailField()
    display_name = serializers.CharField()
    os_type = serializers.CharField()


class IdleTimeApprovalReasonSerializer(BaseModelSerializerCore):

    class Meta:
        model = IdleTimeApprovalReason
        fields = ['id', 'name']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id','email','first_name','last_name']


class IdleTimeApprovalSerializer(BaseModelSerializerCore):
    reason = RelatedFieldAlternative(queryset=IdleTimeApprovalReason.objects.all(), serializer=IdleTimeApprovalReasonSerializer)
    user = RelatedFieldAlternative(queryset=CustomUser.objects.all(), serializer=UserSerializer)
    approved_by = RelatedFieldAlternative(queryset=CustomUser.objects.all(), serializer=UserSerializer,allow_null=True,required=False)
    is_accessible = serializers.SerializerMethodField(read_only=True)

    def get_is_accessible(self, instance):
        return instance.user != self.context['request'].user

    # ref_idle_time = RelatedFieldAlternative(queryset=UserMouseTracking.objects.all(), serializer=UserMouseTrackingSerializer,allow_null=True,required=False)
    class Meta:
        model = IdleTimeApproval
        fields = '__all__'


class APIErrorLogsSerializer(BaseModelSerializerCore):
    class Meta:
        model = APIErrorLogs
        fields = [
            'method',
            'title',
            'trace',
            'path',
            'headers',
            'request_data',
            'response_data',
            'status_code',
            'ip_address',
        ]
        # exclude = ['user']

    def create(self, validated_data):
        return APIErrorLogs.objects.create(user=self.context['user'], **validated_data)

class IdleTimeRequestMultipleSerializer(BaseModelSerializerCore):
    ref_idle_time = RelatedFieldAlternative(queryset=UserMouseTracking.objects.all(), serializer=UserMouseTrackingSerializer,many=True)

    class Meta:
        model = IdleTimeApproval
        fields = ['ref_idle_time', 'reason', 'description']

    def create(self, validated_data):

        description = validated_data.get('description', None)
        reason = validated_data['reason']
        ref_idle_time_ids = validated_data['ref_idle_time']
        created_by = self.context.get('created_by')

        idle_time_approval_list = []
        idle_time_approval = IdleTimeApproval.objects.filter()
        for ref_idle_time_object in ref_idle_time_ids:

            if ref_idle_time_object.idle_time <= Decimal(5.0):

                idle_time_approval_obj = IdleTimeApproval.objects.filter(ref_idle_time=ref_idle_time_object)

                if idle_time_approval_obj:
                    main_idle_time =  idle_time_approval_obj.first().ref_idle_time.idle_time
                    idle_time_req_sum = idle_time_approval_obj.aggregate(Sum('idle_time'))['idle_time__sum']

                    if main_idle_time - idle_time_req_sum > Decimal(0):
                        IdleTimeApproval.objects.create(
                            ref_idle_time=ref_idle_time_object,
                            description= description,
                            reason= reason,
                            user= ref_idle_time_object.user,
                            idle_end_time= ref_idle_time_object.idle_end_time,
                            idle_start_time= ref_idle_time_object.idle_start_time,
                            idle_time= main_idle_time - idle_time_req_sum,
                            status= IdleTimeApproval.approved,
                            created_by= created_by,
                            approved_by= created_by

                        )

                else:
                    print('idle_time_approval_obj', idle_time_approval_obj)

                    IdleTimeApproval.objects.create(
                        ref_idle_time=ref_idle_time_object,
                        description=description,
                        reason=reason,
                        user=ref_idle_time_object.user,
                        idle_end_time=ref_idle_time_object.idle_end_time,
                        idle_start_time=ref_idle_time_object.idle_start_time,
                        idle_time=ref_idle_time_object.idle_time,
                        status=IdleTimeApproval.approved,
                        created_by=created_by,
                        approved_by=created_by

                    )
            else:

                idle_time_approval_obj = IdleTimeApproval.objects.filter(ref_idle_time=ref_idle_time_object)
                if idle_time_approval_obj:
                    main_idle_time = idle_time_approval_obj.first().ref_idle_time.idle_time
                    idle_time_req_sum = idle_time_approval_obj.aggregate(Sum('idle_time'))['idle_time__sum']

                    if main_idle_time - idle_time_req_sum > Decimal(0):
                        IdleTimeApproval.objects.create(
                            ref_idle_time=ref_idle_time_object,
                            description=description,
                            reason=reason,
                            user=ref_idle_time_object.user,
                            idle_end_time=ref_idle_time_object.idle_end_time,
                            idle_start_time=ref_idle_time_object.idle_start_time,
                            idle_time=main_idle_time - idle_time_req_sum,
                            created_by=created_by
                        )

                else:

                    IdleTimeApproval.objects.create(
                        ref_idle_time=ref_idle_time_object,
                        description=description,
                        reason=reason,
                        user=ref_idle_time_object.user,
                        idle_end_time=ref_idle_time_object.idle_end_time,
                        idle_start_time=ref_idle_time_object.idle_start_time,
                        idle_time=ref_idle_time_object.idle_time,
                        created_by=created_by
                    )

            # idle_time_approval_list.append(idle_time_approval)

        return idle_time_approval



