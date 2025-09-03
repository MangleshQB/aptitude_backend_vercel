from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.conf import settings
from app.views.generate_timesheet_excel import generate_CSV
from utils.skype_message import send_skype_message

@shared_task(name="calculate_todays_timesheet")
def calculate_todays_timesheet():
    try:
        status, message = generate_CSV()
        if status:
            message = f'Working hours for the day {message} have been successfully updated.'
        else:
            message = f'Error: {str(message)}'
        surveillance_skype_ids = [settings.SURVEILLANCE_SKYPE_ID]
        send_skype_message(recipient_ids=surveillance_skype_ids, message=message)
    except Exception as e:
        print(e)