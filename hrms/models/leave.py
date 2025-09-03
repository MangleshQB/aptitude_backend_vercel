from app.models import CustomUser
from configuration.models import LeaveTypes
from utils.models import QBBaseModel
from django.db import models

class Leave(QBBaseModel):
    pending = 'pending'
    approve = 'approve'
    rejected = 'rejected'
    cancelled = 'cancelled'

    STATUS_CHOICES = (
        (pending, "Pending"),
        (approve, "Approve"),
        (rejected, "Rejected"),
        (cancelled, "Cancelled"),
    )

    single = 'single'
    multiple = 'multiple'
    first_half = 'first_half'
    second_half = 'second_half'

    duration = (
        (single, 'Single'),
        (multiple, 'Multiple'),
        (first_half, 'First half'),
        (second_half, 'Second half'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    duration_type = models.CharField(max_length=255, choices=duration, default=single)
    leave_type = models.ForeignKey(LeaveTypes, on_delete=models.CASCADE)
    date = models.DateField()
    reporting_status = models.CharField(choices=STATUS_CHOICES, default=pending, max_length=255)
    reporting_approve_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='leave_reporting_approve_by', blank=True, null=True)
    reporting_approve_time = models.DateTimeField(blank=True, null=True)
    status = models.CharField(choices=STATUS_CHOICES, default=pending, max_length=255)
    approve_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='leave_approve_by', blank=True, null=True)
    approve_time = models.DateTimeField(blank=True, null=True)
    description = models.TextField()
    file = models.FileField(upload_to='leave_files/', blank=True, null=True)
    email_message_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.description

    class Meta:
        default_permissions = ["add", "change", "delete", "views", 'all', 'team', "owned"]