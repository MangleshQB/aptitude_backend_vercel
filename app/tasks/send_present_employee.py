from __future__ import absolute_import, unicode_literals
from celery import shared_task
from app.views.send_present_email import send_present
from utils.skype_message import send_skype_message
from django.conf import settings


@shared_task(name="send_present_employee")
def send_present_employee():
    try:
        status, message = send_present()
        if not status:
            message = f'Error: {str(message)}'
        surveillance_skype_ids = [settings.SURVEILLANCE_SKYPE_ID]
        send_skype_message(recipient_ids=surveillance_skype_ids, message=message)
    except Exception as e:
        print(e)

