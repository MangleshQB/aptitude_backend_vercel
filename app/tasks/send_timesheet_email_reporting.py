from __future__ import absolute_import, unicode_literals
from celery import shared_task
from io import BytesIO
from app.models import CustomUser
from tracking.models import EmployeeTimeSheet
from utils.common import get_all_reporting_users
from utils.skype_message import send_skype_message
from django.conf import settings
from datetime import datetime, timedelta, time, date
import pandas as pd
from django.template.loader import get_template
from django.core.mail import EmailMessage

def send_mail_reporting(email):
    status, message = True, ''
    try:
        todays_date = datetime.today().date()
        # all_users = CustomUser.objects.filter(email=email).exclude(email='admin@gmail.com')

        user = CustomUser.objects.filter(email=email).first()
        all_users = get_all_reporting_users(user)

        ignore_emails = ','.join([email, 'admin@gmail.com'])
        all_users = [user for user in all_users if user.email not in ignore_emails]

        data = EmployeeTimeSheet.objects.filter(date=todays_date, user__in=all_users)
        present_user_ids = data.values_list('user_id', flat=True)

        # missing_users = all_users.exclude(id__in=present_user_ids)
        missing_users = [item for item in all_users if item.id not in present_user_ids]

        rmissing_user = []
        print("Absent users:")
        for user in missing_users:
            print(f"User ID: {user.id}, Name: {user.first_name} {user.last_name}")
            rmissing_user.append(f"{user.first_name} {user.last_name}".capitalize())
        rows = []
        for index, excel_data in enumerate(data):
            first_punch_in = datetime.combine(excel_data.date,datetime.strptime(excel_data.first_punch_in,
                                                                                  '%H:%M:%S').time()).strftime(
                '%Y-%m-%d %H:%M:%S')
            try:
                last_punch_out = datetime.combine(excel_data.date,
                                                           datetime.strptime(excel_data.last_punch_out,
                                                                                      '%H:%M:%S').time()).strftime(
                    '%Y-%m-%d %H:%M:%S')
            except:
                last_punch_out = ''

            rows.append({
                '#': index + 1,
                'Date': excel_data.date,
                'User ID': excel_data.user.employee_id,
                'First Name': excel_data.user.first_name,
                'Last Name': excel_data.user.last_name,
                'Total Working Hours': excel_data.total_working_hours,
                'Total Overtime': excel_data.total_over_time,
                'Total Break Time': excel_data.total_break_time,
                'Total Idle Time': excel_data.total_idle_time,
                'First Punch In': first_punch_in,
                'Last Punch Out': last_punch_out,
                'Is Late Coming': excel_data.is_late_coming,
                'Missing Punch In': excel_data.missing_punch_in,
                'Missing Punch Out': excel_data.missing_punch_out,
                'Status': excel_data.status.upper(),
            })

        df = pd.DataFrame(rows)
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name=f"TimeSheet_{todays_date}")
            writer.close()

        buffer.seek(0)

        sender_email = settings.EMAIL_HOST_USER
        recipient_email = [email]
        cc_emails = ['hemal@quantumbot.in']
        # bcc_emails = [""]
        subject = f"{todays_date.strftime('%d-%m-%Y')} - Employee Time Sheet"

        email_body = get_template("timesheet_email.html").render({
            "date": todays_date,
            "absent_users": missing_users,
        })

        email = EmailMessage(subject, email_body, sender_email, recipient_email, cc=cc_emails)
        email.content_subtype = 'html'

        email.attach(f"EmployeeTimeSheet_{todays_date}.xlsx", buffer.getvalue(),
                     'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

        email.send()
        print("Email sent successfully with attachments.")
        message = '\n'.join(rmissing_user)
        return status, message
    except Exception as e:
        status, message = False, str(e)
        return status, message


@shared_task(name="send_timesheet_email_reporting")
def send_timesheet_email_reporting():
    reporting_user_email = ['ceo@aisante.in']
    for email in reporting_user_email:
        try:
            status, message = send_mail_reporting(email)
            if status:
                message = f'Send Mail Successfully For Reporting To This {email}. \n\n Absent Employee: \n{message}'
            else:
                message = f'Error For Reporting To This {email}: {str(message)}'
            surveillance_skype_ids = [settings.SURVEILLANCE_SKYPE_ID]
            send_skype_message(recipient_ids=surveillance_skype_ids, message=message)
        except Exception as e:
            print(e)
