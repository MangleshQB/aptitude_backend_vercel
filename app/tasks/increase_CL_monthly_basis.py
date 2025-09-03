from datetime import date, datetime
from decimal import Decimal
from celery import shared_task
from configuration.models import LeaveTypes, LeaveBalance
from app.models import CustomUser
import calendar


@shared_task(name="increase_CL_monthly_basis")

def increase_CL_monthly_basis():
    now = datetime.now()
    _, last_day = calendar.monthrange(now.year, now.month)
    if now.day == last_day:
        try:

            all_user = CustomUser.objects.filter(is_probation=False).exclude(email='admin@gmail.com')
            leave_type_list = LeaveTypes.objects.filter(is_balance=True)

            cl = LeaveTypes.objects.filter(type=LeaveTypes.casual_Leave).first()
            cl_count = Decimal(cl.limit) / Decimal(12)

            for user in all_user:

                for leave_type in leave_type_list:

                    leavebalance = LeaveBalance.objects.filter(leave_type=leave_type, user=user).first()

                    if leavebalance and leavebalance.leave_type.type == LeaveTypes.casual_Leave:
                        leavebalance.balance = Decimal(leavebalance.balance) + cl_count
                        leavebalance.save()

        except Exception as e:
            print('Error in update leave balance :', e)



