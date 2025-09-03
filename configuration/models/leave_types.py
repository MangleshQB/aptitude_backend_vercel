from django.db import models
from utils.models import QBBaseModel


class LeaveTypes(QBBaseModel):


    casual_Leave = 'CL'
    sick_leave = 'SL'
    leave_without_pay = 'LWP'
    emergency_leave = 'emergency_leave'
    marriage_leave = 'marriage_leave'
    maternity_leave = 'maternity_leave'
    paternity_leave = 'paternity_leave'
    first_half = 'first_half'
    second_half = 'second_half'
    early_leave = 'early_leave'
    late_coming = 'late_coming'
    work_from_home = 'work_from_home'


    leave_choice = (
        (casual_Leave, 'Casual Leave (CL)'),
        (sick_leave, 'Sick Leave (SL)'),
        (leave_without_pay, 'Leave Without Pay (LWP)'),
        (emergency_leave, 'Emergency Leave'),
        (marriage_leave, 'Marriage Leave'),
        (maternity_leave, 'Maternity Leave'),
        (paternity_leave, 'Paternity Leave'),
        (early_leave, 'Early Leave'),
        (late_coming, 'Late Coming'),
        (first_half , 'first_half'),
        (second_half , 'second_half'),
        (work_from_home, 'Work From Home'),
    )
    type = models.CharField(max_length=255, choices=leave_choice, default=leave_without_pay)
    limit = models.PositiveIntegerField(blank=True, null=True)
    start_range = models.PositiveIntegerField(blank=True, null=True)
    end_range = models.PositiveIntegerField(blank=True, null=True)
    el_after = models.TimeField(blank=True, null=True)
    lc_before = models.TimeField(blank=True, null=True)
    wfh_start_time = models.TimeField(blank=True, null=True)
    wfh_end_time = models.TimeField(blank=True, null=True)
    fh_hours = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    sh_hours = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    is_balance = models.BooleanField(default=False)

    def __str__(self):
        return str(self.type)