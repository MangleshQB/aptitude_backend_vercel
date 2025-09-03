from datetime import datetime, timedelta, time, date
from django.utils import timezone
import pytz
from app.models import CustomUser, PersonnelEmployee, IclockTransaction
from django.conf import settings
from django.template.loader import get_template
import os
import pandas as pd
from django.core.mail import EmailMessage
from io import BytesIO
from utils.common import get_all_reporting_users

# TODO send present employee main to ceo
def get_present_employee():
    all_user = CustomUser.objects.all()

    today_date = datetime.strptime(datetime.today().date().strftime("%d/%m/%Y"), "%d/%m/%Y")
    today_date = timezone.make_aware(today_date, timezone=pytz.UTC)
    all_employee_list = []
    for user in all_user:
        try:
            employee_id = int(str(user.employee_id).replace('QB', ''))
            if not employee_id: raise Exception
        except Exception as e:
            continue

        try:
            zkteco_user = PersonnelEmployee.objects.using('zkteco').get(emp_code=employee_id)
            if not zkteco_user:
                raise Exception
        except Exception as e:
            continue

        try:
            IclockTransaction_use = list(IclockTransaction.objects.using('zkteco').filter(
                emp=zkteco_user,
                punch_time__gte=today_date,
                punch_time__lte=today_date + timedelta(days=1),
            ).values('emp_code', 'emp__first_name', 'punch_time', 'punch_state'))
        except Exception as e:
            continue

        temp_dict = {}
        temp_dict['employee_id'] = str(user.employee_id)
        temp_dict['first_name'] = str(user.first_name)
        temp_dict['last_name'] = f'{str(user.last_name) if str(user.last_name) else ""}'

        try:
            punch_time = IclockTransaction_use[0]['punch_time'].strftime('%H:%M:%S')
            punch_state = IclockTransaction_use[0]['punch_state']
            if punch_time and punch_state:
                temp_dict['punch_time'] = punch_time

                all_employee_list.append(temp_dict)
            else:
                raise Exception
        except:
            continue

    return all_employee_list

def send_present_mail(all_employee_list):
    todays_date = datetime.today().date()

    sender_email = settings.EMAIL_HOST_USER
    recipient_email = ["sanjay@quantumbot.in"]
    cc_emails = ['hemal@quantumbot.in']
    subject = f"{todays_date.strftime('%d-%m-%Y')} - Employee Present Sheet"

    email_body = get_template("present_email.html").render({
        "date": todays_date,
        "present_users": all_employee_list,
    })

    email = EmailMessage(subject, email_body, sender_email, recipient_email, cc=cc_emails)

    email.content_subtype = 'html'

    email.send()
    return "The employee present email has been sent successfully."

def send_present():
    status, message = False, ''
    try:
        all_employee_list = get_present_employee()
        if all_employee_list:
            message = send_present_mail(all_employee_list)
            status = True
        else:
            status, message = True, 'No employees are present today.'
    except Exception as e:
        message = str(e)

    return status, message


# TODO send present employee mail to reporting
def get_present_employee_reporting(email):
    user = CustomUser.objects.filter(email=email).first()
    all_user = get_all_reporting_users(user)

    ignore_emails = ','.join([email, 'admin@gmail.com'])
    all_user = [user for user in all_user if user.email not in ignore_emails]

    today_date = datetime.strptime(datetime.today().date().strftime("%d/%m/%Y"), "%d/%m/%Y")
    today_date = timezone.make_aware(today_date, timezone=pytz.UTC)
    all_employee_list = []
    for user in all_user:
        try:
            employee_id = int(str(user.employee_id).replace('QB', ''))
            if not employee_id: raise Exception
        except Exception as e:
            continue

        try:
            zkteco_user = PersonnelEmployee.objects.using('zkteco').get(emp_code=employee_id)
            if not zkteco_user:
                raise Exception
        except Exception as e:
            continue

        try:
            IclockTransaction_use = list(IclockTransaction.objects.using('zkteco').filter(
                emp=zkteco_user,
                punch_time__gte=today_date,
                punch_time__lte=today_date + timedelta(days=1),
            ).values('emp_code', 'emp__first_name', 'punch_time', 'punch_state'))
        except Exception as e:
            continue

        temp_dict = {}
        temp_dict['employee_id'] = str(user.employee_id)
        temp_dict['first_name'] = str(user.first_name)
        temp_dict['last_name'] = f'{str(user.last_name) if str(user.last_name) else ""}'

        try:
            punch_time = IclockTransaction_use[0]['punch_time'].strftime('%H:%M:%S')
            punch_state = IclockTransaction_use[0]['punch_state']
            if punch_time and punch_state:
                temp_dict['punch_time'] = punch_time

                all_employee_list.append(temp_dict)
            else:
                raise Exception
        except:
            continue

    return all_employee_list

def send_present_mail_reporting(all_employee_list, email_reporting):
    todays_date = datetime.today().date()

    sender_email = settings.EMAIL_HOST_USER
    recipient_email = [email_reporting]
    cc_emails = ['hemal@quantumbot.in']
    subject = f"{todays_date.strftime('%d-%m-%Y')} - Employee Present Sheet"

    email_body = get_template("present_email.html").render({
        "date": todays_date,
        "present_users": all_employee_list,
    })

    email = EmailMessage(subject, email_body, sender_email, recipient_email, cc=cc_emails)
    email.content_subtype = 'html'

    email.send()
    return f"Reporting to this {email_reporting}: The employee present email has been sent successfully."

def send_present_reporting(email):
    status, message = False, ''
    try:
        all_employee_list = get_present_employee_reporting(email)
        if all_employee_list:
            message = send_present_mail_reporting(all_employee_list, email)
            status = True
    except Exception as e:
        message = f"Reporting to this {email}: {str(e)}"

    return status, message