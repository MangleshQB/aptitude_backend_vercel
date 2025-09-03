from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import exception_handler
from app.models import CustomUser
from django.conf import settings
from django.template.loader import get_template
from app.models import Leaves
from datetime import timedelta
from django.db.models import Count
from configuration.models import Holiday

def validate_file_size(value):
    file_size = value.size

    if file_size > 5242880:
        raise ValidationError("You cannot upload file more than 5Mb")
    else:
        return value


class SetPagination(PageNumberPagination):
    page = 1
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100



    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'page': int(self.request.GET.get('page', 1)),
            'page_size': int(self.request.GET.get('page_size', self.page_size)),
            'data': data,
            'message': 'success',
            'status': True
        })


class ResponseFormat(object):
    def __init__(self, user=None, **args):
        self.response = {
            "status": args.get('status', True),
            "error": args.get('error', 200),
            "data": args.get('data', []),
            "message": args.get('message', 'success')
        }


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        response.data = {
            "status": False,
            "error": response.status_text,
            "data": [],
            "message": response.data,
        }
    return response


class RelatedFieldAlternative(serializers.PrimaryKeyRelatedField):

    def __init__(self, **kwargs):
        self.serializer = kwargs.pop("serializer", None)
        if self.serializer is not None and not issubclass(
                self.serializer, serializers.Serializer
        ):
            raise TypeError('"serializer" is not a valid serializer class')

        super().__init__(**kwargs)

    def use_pk_only_optimization(self):
        return False if self.serializer else True

    def to_representation(self, instance):
        if self.serializer:
            return self.serializer(instance, context=self.context).data
        return super().to_representation(instance)


def get_all_reporting_users(user, req_user=True):

    direct_reports = CustomUser.objects.filter(reporting_to=user)
    all_reporting_users = set(direct_reports)
    if user not in all_reporting_users and req_user:
        all_reporting_users.add(user)

    for report in direct_reports:
        all_reporting_users.update(get_all_reporting_users(report, req_user=False))

    return list(all_reporting_users)


def send_email(template=None, subject="", recipient_email=None, cc_emails=None, bcc_emails=None, body_context=None,
               is_html=False):
    try:
        if not recipient_email:
            raise ValueError("Recipient email address is required.")

        sender_email = settings.EMAIL_HOST_USER

        if template:
            try:
                email_body = get_template(template).render(body_context)
            except Exception as e:
                print(f"Error rendering email template: {e}")
                raise ValueError("Invalid email template or context.")
        else:
            email_body = body_context.get("body", "") if body_context else ""

        email = EmailMessage(
            subject=subject,
            body=email_body,
            from_email=sender_email,
            to=recipient_email,
            cc=cc_emails,
            bcc=bcc_emails,
        )

        if is_html:
            email.content_subtype = "html"
        email.send()

        # Retrieve Message-ID
        message_id = email.message().get("Message-ID")
        print(f"Message-ID: {message_id}")

        return message_id  # Return the Message-ID if needed

    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def reply_email(template=None, original_message_id=None, body_context=None, is_html=False):
    try:
        if not original_message_id:
            raise ValueError("Original Message-ID is required to send a reply.")

        sender_email = settings.EMAIL_HOST_USER

        if template:
            try:
                email_body = get_template(template).render(body_context)
            except Exception as e:
                print(f"Error rendering email template: {e}")
                raise ValueError("Invalid email template or context.")
        else:
            email_body = body_context.get("body", "") if body_context else ""

        email = EmailMessage(
            body=email_body,
            from_email=sender_email,
        )

        email.extra_headers = {
            "In-Reply-To": original_message_id,
            "References": original_message_id,
         }
        print(f"Sending reply to message ID: {original_message_id}")
        if is_html:
            email.content_subtype = "html"

        email.send()

        reply_message_id = email.message().get("Message-ID")
        print(f"Reply Message-ID: {reply_message_id}")

        return reply_message_id

    except Exception as e:
        print(f"Error replying to email: {e}")
        return None

def get_crm_leave(email, start_date, end_date):
    try:
        leave_data = list(Leaves.objects.filter(user__email=email, status='approved',
                                                leave_date__range=[start_date, end_date + timedelta(days=1)]).using(
            'crm').values('leave_type__type_name', 'duration').annotate(count=Count('leave_type__type_name')))
        if not leave_data: raise Exception
    except Exception as e:
        leave_data = []

    half_day, leave_taken, paid_leave, lwp, SL, CL = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
    if leave_data:
        for levae in leave_data:
            label = levae['leave_type__type_name']
            duration = levae['duration']
            if 'LWP' in label:
                if 'half' in duration:
                    lwp += float(levae['count']) / 2
                else:
                    lwp += float(levae['count'])
            elif '(PL)' in label:
                if 'half' in duration:
                    paid_leave += float(levae['count']) / 2
                else:
                    paid_leave += float(levae['count'])
            elif '(SL)' in label:
                if 'half' in duration:
                    SL += float(levae['count']) / 2
                else:
                    SL += float(levae['count'])
            elif '(CL)' in label:
                if 'half' in duration:
                    CL += float(levae['count']) / 2
                else:
                    CL += float(levae['count'])
            else:
                continue
            if 'half' in duration:
                leave_taken += float(levae['count']) / 2
                half_day += float(levae['count']) / 2
            else:
                leave_taken += float(levae['count'])

    return half_day, leave_taken, paid_leave, lwp, SL, CL


def get_holidays(start_date, end_date):
    all_holidays = Holiday.objects.filter(leave_date__range=[start_date, end_date + timedelta(days=1)])
    print("all_holidays , ", all_holidays)