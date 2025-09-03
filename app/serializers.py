from decimal import Decimal

import pytz
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group, Permission
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from datetime import datetime, timedelta, date

from configuration.models import LeaveTypes, LeaveBalance, Holiday
from tracking.models import EmployeeTimeSheet
from utils.common import RelatedFieldAlternative
from utils.serializer import BaseModelSerializerCore
from .models import Designation, CustomUser
from django.db.models import Sum, F

class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    is_software = serializers.BooleanField(required=False, default=False)


class DesignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designation
        fields = '__all__'


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'

class CustomUserSerializer(BaseModelSerializerCore):
    designation = RelatedFieldAlternative(queryset=Designation.objects.all(), serializer=DesignationSerializer)
    groups = RelatedFieldAlternative(queryset=Group.objects.all(), serializer=GroupSerializer, many=True)
    password = serializers.CharField(required=False, write_only=True)
    is_surveillance_active = serializers.BooleanField(required=False)
    reporting_to = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), many=False, required=False)
    is_screenshot_active = serializers.BooleanField(required=False)
    working_hours = serializers.SerializerMethodField()

    def get_working_hours(self, obj):

        start_date_str = self.context.get('start_date')
        end_date_str = self.context.get('end_date')
        if start_date_str and end_date_str:
            try:
                start_date = datetime.strptime(start_date_str, "%d/%m/%Y")
                end_date = datetime.strptime(end_date_str, "%d/%m/%Y")
            except ValueError:
                raise serializers.ValidationError("Invalid date format. Use  DD/MM/YYYY.")
        else:
            now = datetime.now()
            start_date = now.replace(day=1)
            end_date = (now.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

        timesheets = EmployeeTimeSheet.objects.filter(
            user=obj,
            date__range=[start_date, end_date]
        ).values_list('total_working_hours', 'total_break_time', 'total_idle_time')


        total_working_hours = timedelta()
        total_break_time = timedelta()
        total_idle_time = timedelta()

        for working_hours, break_time, idle_time in timesheets:
            total_working_hours += self._parse_time(working_hours)
            total_break_time += self._parse_time(break_time)
            total_idle_time += self._parse_time(idle_time)
            # total_idle_time += float(idle_time) or 0.0

        return {
            "total_working_hours": self._format_timedelta(total_working_hours),
            "total_break_time": self._format_timedelta(total_break_time),
            # "total_idle_time": self._format_float_to_hhmmss(total_idle_time)
            "total_idle_time": self._format_timedelta(total_idle_time)
        }

    @staticmethod
    def _parse_time(time_str):

        if not time_str or str(time_str).count(':') != 2:
            return timedelta()
        hours, minutes, seconds = map(int, time_str.split(':'))
        return timedelta(hours=hours, minutes=minutes, seconds=seconds)

    @staticmethod
    def _format_timedelta(td):

        total_seconds = int(td.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    @staticmethod
    def _format_float_to_hhmmss(float_hours):
        if float_hours:
            print()
        total_seconds = int(float_hours * 60)
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'designation', 'profile_image', 'email', 'password', 'first_name', 'last_name', 'phone_number', 'is_active', 'is_staff', 'is_superuser', 'groups', 'is_surveillance_active', 'reporting_to','employee_id','is_screenshot_active', 'joining_date', 'date_of_birth', 'is_probation', 'working_hours']
        depth = 1

    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        validated_data['password'] = make_password(password)
        validated_data['username'] = validated_data['email']
        user = super(CustomUserSerializer, self).create(validated_data)

        leave_type_list = LeaveTypes.objects.filter(is_balance=True)
        # user_context = self.context.get('user')
        for leave_type in leave_type_list:
            if not validated_data['is_probation'] and leave_type.type == LeaveTypes.sick_leave:
                sick_leave = LeaveTypes.objects.filter(type=LeaveTypes.sick_leave).first().limit
                LeaveBalance.objects.create(leave_type=leave_type, user=user, balance=Decimal(sick_leave))
            LeaveBalance.objects.create(leave_type=leave_type, user=user)

        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        if 'is_probation' in validated_data:
            if instance.is_probation and not validated_data['is_probation']:
                #  true                           #false
                sick_leave = LeaveTypes.objects.filter(type=LeaveTypes.sick_leave).first().limit
                leave_balance = LeaveBalance.objects.filter(user=instance,leave_type__type=LeaveTypes.sick_leave).first()
                leave_balance.balance = Decimal(sick_leave)
                print('------------------------------------> if instance.is_probation and not validated_data["is_probation"]')
                leave_balance.save()
            elif not instance.is_probation and validated_data['is_probation']:
                #       false                         true
                leave_balance = LeaveBalance.objects.filter(user=instance, leave_type__type=LeaveTypes.sick_leave).first()
                leave_balance.balance = Decimal(0)
                print("-------------------------------------> elif not instance.is_probation and validated_data['is_probation']:")
                leave_balance.save()

        if validated_data.get('email', None) is not None:
            validated_data['username'] = validated_data.get('email', None)


        update = super(CustomUserSerializer, self).update(instance, validated_data)
        if password:
            password = make_password(password)
            update.password = password
            update.save()
        return update




class CustomUserWithHoursSerializer(serializers.ModelSerializer):
    designation = RelatedFieldAlternative(queryset=Designation.objects.all(), serializer=DesignationSerializer)
    groups = RelatedFieldAlternative(queryset=Group.objects.all(), serializer=GroupSerializer, many=True)
    password = serializers.CharField(required=False, write_only=True)
    is_surveillance_active = serializers.BooleanField(required=False)
    reporting_to = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), many=False, required=False)
    is_screenshot_active = serializers.BooleanField(required=False)
    working_hours = serializers.SerializerMethodField()

    class Meta:

        model = CustomUser
        fields = [
            'id', 'username', 'designation', 'email', 'password', 'first_name', 'last_name',
            'phone_number', 'is_active', 'is_staff', 'is_superuser', 'groups', 'is_surveillance_active',
            'reporting_to', 'employee_id', 'is_screenshot_active', 'working_hours'
        ]
        depth = 1

    def get_working_hours(self, obj):

        start_date_str = self.context.get('start_date')
        end_date_str = self.context.get('end_date')
        if start_date_str and end_date_str:
            try:
                start_date = datetime.strptime(start_date_str, "%d/%m/%Y")
                end_date = datetime.strptime(end_date_str, "%d/%m/%Y")
            except ValueError:
                raise serializers.ValidationError("Invalid date format. Use  DD/MM/YYYY.")
        else:
            now = datetime.now()
            start_date = now.replace(day=1)
            end_date = (now.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

        timesheets = EmployeeTimeSheet.objects.filter(
            user=obj,
            date__range=[start_date, end_date]
        ).values_list('total_working_hours', 'total_break_time', 'total_idle_time')


        total_working_hours = timedelta()
        total_break_time = timedelta()
        total_idle_time = timedelta()

        for working_hours, break_time, idle_time in timesheets:
            total_working_hours += self._parse_time(working_hours)
            total_break_time += self._parse_time(break_time)
            total_idle_time += self._parse_time(idle_time)
            # total_idle_time += float(idle_time) or 0.0

        return {
            "total_working_hours": self._format_timedelta(total_working_hours),
            "total_break_time": self._format_timedelta(total_break_time),
            # "total_idle_time": self._format_float_to_hhmmss(total_idle_time)
            "total_idle_time": self._format_timedelta(total_idle_time)
        }

    @staticmethod
    def _parse_time(time_str):

        if not time_str or str(time_str).count(':') != 2:
            return timedelta()
        hours, minutes, seconds = map(int, time_str.split(':'))
        return timedelta(hours=hours, minutes=minutes, seconds=seconds)

    @staticmethod
    def _format_timedelta(td):

        total_seconds = int(td.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    @staticmethod
    def _format_float_to_hhmmss(float_hours):
        if float_hours:
            print()
        total_seconds = int(float_hours * 60)
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

class CustomUserSerializerForPermission(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'phone_number', 'email','username', 'is_active','is_superuser']



class UpcomingThisMonthHolidaySerializer(serializers.ModelSerializer):
    type = serializers.CharField(source='get_type_display')
    in_days = serializers.SerializerMethodField()
    class Meta:
        model = Holiday
        fields = ['name', 'date', 'description', 'type', 'in_days']
    def get_in_days(self, obj):
        print("obj",obj)
        return (obj.date - date.today()).days