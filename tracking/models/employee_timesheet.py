from django.db import models

from app.models import CustomUser
from utils.models import QBBaseModel
import os

class EmployeeTimeSheet(QBBaseModel):
    PRESENT = "present"
    HALFDAY = "half_day"
    ABSENT = "absent"

    TYPE_OF_STATUS = (
        (PRESENT, "Present"),
        (HALFDAY, 'Half Day'),
        (ABSENT, 'Absent'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date = models.DateField()
    total_effective_hours = models.CharField(max_length=255, default='0')
    total_working_hours = models.CharField(max_length=255, default='0')
    total_over_time = models.CharField(max_length=255, default='0')
    total_break_time = models.CharField(max_length=255, default='0')
    total_idle_time = models.CharField(max_length=255, default='0')
    total_approved_idle_time = models.CharField(max_length=255, default='0')
    first_punch_in = models.CharField(max_length=255)
    last_punch_out = models.CharField(max_length=255, blank=True, null=True)

    is_late_coming = models.BooleanField(default=False)
    missing_punch_in = models.BooleanField(default=False)
    missing_punch_out = models.BooleanField(default=False)
    status = models.CharField(choices=TYPE_OF_STATUS, max_length=255, default=PRESENT)
