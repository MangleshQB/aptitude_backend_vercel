from __future__ import absolute_import, unicode_literals
from celery import shared_task
from app.views.generate_timesheet_excel import generate_CSV
from utils.skype_message import send_skype_message
from django.conf import settings


@shared_task(name="send_timesheet_email")
def send_timesheet_email():
    try:
        status, message = generate_CSV(send_mail=True)
        if status:
            message = f'Send Mail Successfully. \n\n Absent Employee: \n{message}'
        else:
            message = f'Error: {str(message)}'
        surveillance_skype_ids = [settings.SURVEILLANCE_SKYPE_ID]
        send_skype_message(recipient_ids=surveillance_skype_ids, message=message)
    except Exception as e:
        print(e)
