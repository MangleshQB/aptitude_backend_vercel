from __future__ import absolute_import, unicode_literals
import os
from celery import Celery, Task
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")
app = Celery('main', broker=settings.CELERY_BROKER_URL, include=['app.tasks'])
app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()


app.conf.beat_schedule = {

    'send_timesheet_email': {
        'task': 'send_timesheet_email',
        'schedule': crontab(minute="0", hour="20")
    },
    'send_timesheet_email_reporting': {
        'task': 'send_timesheet_email_reporting',
        'schedule': crontab(minute="10", hour="20")
    },
    'calculate_todays_timesheet': {
        'task': 'calculate_todays_timesheet',
        'schedule': crontab(minute="50", hour="23")
    },
    'send_present_employee': {
            'task': 'send_present_employee',
            'schedule': crontab(minute="30", hour="12")
    },
    'send_present_employee_reporting': {
            'task': 'send_present_employee_reporting',
            'schedule': crontab(minute="30", hour="12")
    },
    'upcoming_holiday_list': {
                'task': 'upcoming_holiday_list',
                'schedule': crontab(minute="00", hour="10", day_of_month='28-31')
    },
    'send_anniversary_message': {
                'task': 'send_anniversary_message',
                'schedule': crontab(minute="00", hour="10")
    },
    'send_birthday_message': {
            'task': 'send_birthday_message',
            'schedule': crontab(minute="00", hour="10")
    },
    # 'increase_CL_monthly_basis': {
    #     'task': 'increase_CL_monthly_basis',
    #     'schedule': crontab(minute="50", hour="25", day_of_month='28-31')
    # },

}