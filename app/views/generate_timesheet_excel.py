from io import BytesIO

from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import get_template
import os
import pandas as pd
from tracking.models import EmployeeTimeSheet
from .daily_working_hours_calculate import calculate_work_hours
from ..models import CustomUser

from datetime import datetime, timedelta, time, date
from django.utils import timezone

def generate_CSV(send_mail=False):
    status, message = True, ''
    try:
        message = calculate_work_hours()
        if send_mail and message:
            todays_date = datetime.today().date()
            # all_users = CustomUser.objects.all()
            all_users = CustomUser.objects.exclude(email='admin@gmail.com')

            data = EmployeeTimeSheet.objects.filter(date=todays_date)
            present_user_ids = data.values_list('user_id', flat=True)

            missing_users = all_users.exclude(id__in=present_user_ids)

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
            recipient_email = ["sanjay@quantumbot.in"]
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

        return status, message
    except Exception as e:
        status, message = False, str(e)
        return status, message
