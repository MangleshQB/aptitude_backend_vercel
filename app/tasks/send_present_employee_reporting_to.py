from __future__ import absolute_import, unicode_literals
from celery import shared_task
from app.views.send_present_email import send_present_reporting
from utils.skype_message import send_skype_message
from django.conf import settings


@shared_task(name="send_present_employee_reporting")
def send_present_employee_reporting():
    reporting_user_email = ['ceo@aisante.in']
    for email in reporting_user_email:
        try:
            status, message = send_present_reporting(email=email)
            if not status:
                message = f'Error: {str(message)}'
            surveillance_skype_ids = [settings.SURVEILLANCE_SKYPE_ID]
            send_skype_message(recipient_ids=surveillance_skype_ids, message=message)
        except Exception as e:
            print(e)

