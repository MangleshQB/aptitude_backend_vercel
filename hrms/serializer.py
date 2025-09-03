from datetime import timedelta
from decimal import Decimal
from app.tasks.async_send_mail import send_email
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from app.models import CustomUser, Designation
from app.serializers import CustomUserSerializerForPermission, DesignationSerializer
from configuration.models import Holiday, LeaveTypes, LeaveBalance
from configuration.models.ticket_subcategory import TicketSubCategory
from configuration.models.ticket_category import TicketCategory
from configuration.serializers import TicketCategorySerializer, TicketSubCategorySerializer, LeaveTypesSerializer
from hrms.models import Ticket, KnowledgeBaseCategory, KnowledgeBase,KnowledgeBaseFile,Leave
from hrms.models.knowledge_base import knowledge_files_name
from utils.serializer import BaseModelSerializerCore, RefUserSerializer
from utils.common import RelatedFieldAlternative
from django.conf import settings


class TicketSerializer(BaseModelSerializerCore):
    category = RelatedFieldAlternative(queryset=TicketCategory.objects.all(), serializer=TicketCategorySerializer, many=False)
    sub_category = RelatedFieldAlternative(queryset=TicketSubCategory.objects.all(), serializer=TicketSubCategorySerializer, many=False)
    assigned_to = RelatedFieldAlternative(queryset=CustomUser.objects.all(), serializer=CustomUserSerializerForPermission, many=False, allow_null=True, allow_empty=True, required=False)
    code = serializers.CharField(read_only=True)
    is_accessible = serializers.SerializerMethodField(read_only=True)

    def get_is_accessible(self, instance):
        if self.context['request'].user in instance.notify_to.all():
            return True
        return False


    class Meta:
        model = Ticket
        fields = '__all__'

    def create(self, validated_data):
        instance = super().create(validated_data)
        instance.code = f"tk_00{instance.id}"

        if validated_data.get('category', None):
            notify_user = validated_data.get('category').notify_to.all().values_list('id', flat=True)
            instance.notify_to.set(notify_user)
            instance.save()

        category = validated_data.get('category')
        if category:
            notify_users = list(category.notify_to.exclude(email='admin@gmail.com').values_list('email', flat=True))

            if notify_users:
                send_email.delay(
                    is_html=True,
                    template='ticket_mail.html',
                    subject=f"New Support Ticket Created: {validated_data.get('title')}",
                    cc_emails=[self.context['created_by'].email],
                    recipient_email=notify_users,
                    body_context={
                        'title': validated_data.get('title'),
                        'category': validated_data.get('category').name,
                        'sub_category': validated_data.get('sub_category').name,
                        'description': validated_data.get('description'),
                        'priorities': validated_data.get('priorities'),
                        'status': Ticket.pending,
                        'created_by': f'{self.context["created_by"].first_name} {self.context["created_by"].last_name}',
                        'assigned_to': validated_data.get('assigned_to', None).first_name if validated_data.get('assigned_to', None) else '',
                    }
                )
        return instance

    def update(self, instance, validated_data):
        previous_status = instance.status
        instance = super().update(instance, validated_data)
        instance.save()

        if 'status' in validated_data and validated_data['status'] != previous_status:
            notify_users = list(instance.category.notify_to.exclude(email='admin@gmail.com').values_list('email', flat=True))
            if notify_users:
                send_email.delay(
                    is_html=True,
                    template='ticket_mail.html',
                    subject=f"Ticket Update: {validated_data.get('title')}",
                    cc_emails=[instance.created_by.email, instance.updated_by.email],
                    recipient_email=notify_users,
                    body_context={
                        'title': validated_data.get('title'),
                        'category': validated_data.get('category').name,
                        'sub_category': validated_data.get('sub_category').name,
                        'description': validated_data.get('description'),
                        'priorities': validated_data.get('priorities'),
                        'status': validated_data.get('status'),
                        'updated_by': f'{instance.updated_by.first_name} {instance.updated_by.last_name}',
                        'created_by': f'{instance.created_by.first_name} {instance.created_by.last_name}',
                        'assigned_to': validated_data.get('assigned_to', None).first_name if validated_data.get('assigned_to', None) else '',
                        'edit_ticket' : True
                    })

        return instance


class KnowledgeBaseCategorySerializer(BaseModelSerializerCore):

    class Meta:
        model = KnowledgeBaseCategory
        fields = '__all__'


class KnowledgeBaseFileSerializer(BaseModelSerializerCore):
    # class Meta:
        model = KnowledgeBaseFile
        fields = '__all__'


class KnowledgeBaseSerializer(BaseModelSerializerCore):

    category = RelatedFieldAlternative(queryset=KnowledgeBaseCategory.objects.all(),
                                       serializer=KnowledgeBaseCategorySerializer, many=False)


    class Meta:
        model = KnowledgeBase
        fields = '__all__'

    # def create(self, validated_data):
    #     designation = validated_data.pop('designation')
    #     knowledge_base = KnowledgeBase.objects.create(**validated_data)
    #     knowledge_base.designation.set(designation)
    #     return knowledge_base





class LeaveSerializer(BaseModelSerializerCore):
    user = RelatedFieldAlternative(queryset=CustomUser.objects.all(), serializer=RefUserSerializer)
    start_date = serializers.DateField(write_only=True)
    end_date = serializers.DateField(write_only=True)
    date = serializers.DateField(read_only=True)
    leave_type = RelatedFieldAlternative(queryset=LeaveTypes.objects.all(), serializer=LeaveTypesSerializer)
    get_hr_email = settings.HR_EMAIL

    class Meta:
        model = Leave
        fields = '__all__'
        depth = 1


    @transaction.atomic
    def create(self, validated_data):
        start_date = validated_data.pop('start_date')
        end_date = validated_data.pop('end_date')
        user = validated_data['user']
        leave_type = validated_data['leave_type']
        duration_type = validated_data.get('duration_type', None)


        all_dates = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]

        holidays = set(Holiday.objects.filter(date__in=all_dates).values_list('date', flat=True))
        valid_dates = [date for date in all_dates if date not in holidays]

        existing_leave_dates = set(Leave.objects.filter(user=user, date__in=valid_dates).values_list('date', flat=True))
        valid_dates = [date for date in valid_dates if date not in existing_leave_dates]

        valid_dates = [date for date in valid_dates if date.weekday() not in (5, 6)]

        leaves = []
        if leave_type.is_balance:
            leave_balance = LeaveBalance.objects.filter(user=user, leave_type=leave_type).first()

            if duration_type and 'half' in duration_type:
                input_balance =  Decimal(len(valid_dates))/Decimal(2)
            else:
                input_balance =  Decimal(len(valid_dates))

            if not leave_balance or not leave_balance.balance > input_balance:
                raise ValidationError(f"You do not have enough leave balance. The maximum balance allowed is {leave_balance.balance}.")

            if duration_type and 'half' in duration_type:
                leave_balance.balance = Decimal(leave_balance.balance) - Decimal(len(valid_dates)/2)
            else:
                leave_balance.balance = Decimal(leave_balance.balance) - Decimal(len(valid_dates))

            leave_balance.save()

        for date in valid_dates:
            leave_data = validated_data
            leave_data['date'] = date
            leave = super().create(leave_data)
            leaves.append(leave)
        # print('send mail>>>>>',self.get_hr_email,user.reporting_to.email,user.email)
        leave_date_list = ', '.join([date.strftime('%Y-%m-%d') for date in valid_dates])
        if leaves:
            send_email.delay(
                is_html=True,
                template='leave_mail.html',
                subject="Leave applied",
                recipient_email=[user.email],
                cc_emails=[self.get_hr_email,user.reporting_to.email],
                body_context={"leave_date":leave_date_list,"instance":leaves[-1]}
            )
            return leaves[-1]


    def update(self, instance, validated_data):
        # print('instance', instance)
        # print('validated_data', validated_data)
        mail_data ={}
        if 'reporting_status' in validated_data: #and validated_data['reporting_status'] == Leave.approve:
            instance.reporting_approve_by = self.context['updated_by']
            instance.reporting_approve_time = timezone.now()
            mail_data = {
                "subject":f"Leave {validated_data['reporting_status']} by TL.",
                "recipient_email":[self.get_hr_email],
                "cc_emails":[instance.user.email,instance.user.reporting_to.email],
                "body_context":{"approved_by": "TL","leave_status":validated_data['reporting_status'],"instance":instance},
            }
        if 'status' in validated_data: # and validated_data['status'] == Leave.approve:
            status = validated_data['status']

            if status == Leave.approve and instance.reporting_status != Leave.approve:
                raise serializers.ValidationError(
                    {"status": "Status cannot be approved unless reporting_status is approved."}
                )
            if status != Leave.approve:
                leave_balance = LeaveBalance.objects.filter(user=instance.user, leave_type=instance.leave_type).first()
                if leave_balance:
                    # print('instance>>>>',instance.duration_type)
                    if instance.duration_type and 'half' in str(instance.duration_type):
                        leave_balance.balance += Decimal(0.5)
                    else:
                        leave_balance.balance += 1
                    leave_balance.save()

            mail_data = {
                "subject":f"Leave {validated_data['status']} by HR.",
                "recipient_email":[instance.user.email],
                "cc_emails":[self.get_hr_email,instance.user.reporting_to.email],
                "body_context":{"approved_by": "HR","leave_status":validated_data['status'],"instance":instance},
            }


        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()

        send_email.delay(
            is_html=True,
            template='leave_mail_replay.html',
            subject=mail_data["subject"],
            recipient_email=mail_data["recipient_email"],
            cc_emails=mail_data["cc_emails"],
            body_context=mail_data["body_context"]
        )
        return instance

