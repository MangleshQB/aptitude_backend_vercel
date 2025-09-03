from django.utils import timezone
from rest_framework import serializers
from datetime import timedelta

from app.models import CustomUser
from configuration.models import SoftwareConfiguration, App_Version, Holiday, LeaveTypes, LeaveBalance, \
    TicketCategory, TicketSubCategory, SoftwareProcess, UserAppVersion
from hrms.models.knowledge_base import KnowledgeBaseCategory
from hrms.models.ticket import Ticket
from utils.common import RelatedFieldAlternative
from utils.serializer import BaseModelSerializerCore
from django.db import transaction


class ConfigurationSerializer(BaseModelSerializerCore):
    class Meta:
        model = SoftwareConfiguration
        fields = '__all__'

class HolidaySerializer(BaseModelSerializerCore):
    class Meta:
        model = Holiday
        fields = ['id', 'name', 'date', 'type', 'description', 'repeats_annually']


class AppVersionSerializer(BaseModelSerializerCore):
    exe = serializers.FileField(use_url=True)

    class Meta:
        model = App_Version
        fields = ['id', 'created_at', 'updated_at', 'is_active', 'is_deleted', 'deleted_at', 'version', 'exe', 'created_by', 'updated_by', 'deleted_by', 'system_os','description']


class LeaveTypesSerializer(BaseModelSerializerCore):

    class Meta:
        model = LeaveTypes
        fields = '__all__'

    def validate(self, data):
        if self.context.get("created_by", None):
            data['created_by'] = self.context.get("created_by")
        if self.context.get("updated_by", None):
            data['updated_by'] = self.context.get("updated_by")
        type = data.get('type', None)

        if type is not None:

            if type == LeaveTypes.casual_Leave or type == LeaveTypes.sick_leave :
                if not data.get('limit', None):
                    raise serializers.ValidationError('You must specify a limit.')
                data['limit'] = int(data.get('limit', None))
                data['start_range'] = None
                data['end_range'] = None
                data['el_after'] = None
                data['lc_before'] = None
                data['wfh_start_time'] = None
                data['wfh_end_time'] = None
                data['fh_hours'] = None
                data['sh_hours'] = None


            elif type == LeaveTypes.marriage_leave or LeaveTypes.maternity_leave or LeaveTypes.paternity_leave:
                if not data.get('start_range', None) or not data.get('end_range', None):
                    raise serializers.ValidationError('You must specify start and end range.')
                data['start_range'] = int(data.get('start_range', None))
                data['end_range'] = int(data.get('end_range', None))
                data['limit'] = None
                data['el_after'] = None
                data['lc_before'] = None
                data['wfh_start_time'] = None
                data['wfh_end_time'] = None
                data['fh_hours'] = None
                data['sh_hours'] = None

            elif type == LeaveTypes.early_leave:
                if not data.get('el_after', None):
                    raise serializers.ValidationError('You must specify early leave time.')
                data['el_after'] = data.get('el_after', None)
                data['limit'] = None
                data['start_range'] = None
                data['end_range'] = None
                data['lc_before'] = None
                data['wfh_start_time'] = None
                data['wfh_end_time'] = None
                data['fh_hours'] = None
                data['sh_hours'] = None
            elif type == LeaveTypes.late_coming:
                if not data.get('lc_before', None):
                    raise serializers.ValidationError('You must specify late coming before time.')
                data['lc_before'] = data.get('lc_before', None)
                data['limit'] = None
                data['start_range'] = None
                data['end_range'] = None
                data['el_after'] = None
                data['wfh_start_time'] = None
                data['wfh_end_time'] = None
                data['fh_hours'] = None
                data['sh_hours'] = None
            elif type == LeaveTypes.work_from_home:
                if not data.get('wfh_start_time', None) or not data.get('wfh_end_time', None):
                    raise serializers.ValidationError('You must specify WFH Start Time and WFH End Time.')
                data['wfh_start_time'] = data.get('wfh_start_time', None)
                data['wfh_end_time'] = data.get('wfh_end_time', None)
                data['limit'] = None
                data['start_range'] = None
                data['end_range'] = None
                data['el_after'] = None
                data['lc_before'] = None
                data['fh_hours'] = None
                data['sh_hours'] = None
            elif type == LeaveTypes.fh_hours or type == LeaveTypes.sh_hours:
                data['fh_hours'] = data.get('fh_hours', None)
                data['sh_hours'] = data.get('sh_hours', None)
                data['limit'] = None
                data['start_range'] = None
                data['end_range'] = None
                data['el_after'] = None
                data['lc_before'] = None
                data['wfh_start_time'] = None
                data['wfh_end_time'] = None

        return data




class LeaveBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveBalance
        fields = ['id', 'leave_type', 'user', 'balance', 'total']



class TicketSubCategorySerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    id = serializers.IntegerField(required=False)


    class Meta:
        model = TicketSubCategory
        fields = ['id', 'name', 'created_by', 'updated_by']



class CustomuserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name']



class TicketCategorySerializer(BaseModelSerializerCore):

    ticket_subcategory = TicketSubCategorySerializer(many=True, write_only=True)
    sub_category = serializers.SerializerMethodField()

    def get_sub_category(self, instance):
        return TicketSubCategorySerializer(instance.ticket_subcategory_category.all(), many=True).data

    notify_to = RelatedFieldAlternative(queryset=CustomUser.objects.all(), serializer=CustomuserSerializer ,many=True )

    class Meta:
        model = TicketCategory
        fields = ['id', 'name','sub_category','notify_to','ticket_subcategory','created_by','updated_by','is_active']

    @transaction.atomic
    def create(self, validated_data):


        sub_categorys = validated_data.pop('ticket_subcategory')
        notify_to = validated_data.pop('notify_to')
        ticket_category = TicketCategory.objects.create(**validated_data)
        ticket_category.notify_to.set(notify_to)
        ticket_category.save()

        for sub_category in sub_categorys:
            id = sub_category.get('id', None)
            name = sub_category.get('name', None)

            if id:continue
            if name:
                TicketSubCategory.objects.create(name=name, category=ticket_category, created_by=self.context['created_by'])

        return ticket_category


class SoftwareProcessSerializer(BaseModelSerializerCore):
    class Meta:
        model = SoftwareProcess
        fields = '__all__'


class UserAppVersionSerializer(BaseModelSerializerCore):
    class Meta:
        model = UserAppVersion
        fields = '__all__'

    def create(self, validated_data):
        # validated_data['user'] = self.context['user']
        user = validated_data.pop('user')
        return UserAppVersion.objects.update_or_create(user=user, defaults=validated_data)[0]
        # return UserAppVersion.objects.get_or_create(**validated_data)[0]