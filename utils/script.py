from decimal import Decimal

from app.models import CustomUser
from configuration.models import LeaveTypes, LeaveBalance


def all_user():
    all_user = CustomUser.objects.filter().exclude(email='admin@gmail.com')
    for user in all_user:
        print('user :',user.email)

        leave_type_list = LeaveTypes.objects.filter(is_balance=True)
        for leave_type in leave_type_list:
            leavebalance = LeaveBalance.objects.get_or_create(leave_type=leave_type, user=user)


def update_leave_balance():
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

