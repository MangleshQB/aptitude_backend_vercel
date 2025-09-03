from django.db import models

from app.models import CustomUser
from utils.models import QBBaseModel
from .user_mouse_tracking import UserMouseTracking

class IdleTimeApprovalReason(QBBaseModel):

    name = models.CharField(max_length=255, blank=False, null=False)


class IdleTimeApproval(QBBaseModel):

    pending = 'pending'
    approved = 'approved'
    rejected = 'rejected'

    status_choices = (
        (pending, 'Pending'),
        (approved, 'Approved'),
        (rejected, 'Rejected'),
    )

    ref_idle_time = models.ForeignKey(UserMouseTracking, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=255,choices=status_choices, default=pending)
    reason = models.ForeignKey(IdleTimeApprovalReason, on_delete=models.CASCADE)
    idle_time = models.DecimalField(max_digits=10,decimal_places=2,blank=True, null=True)
    approved_time = models.DateTimeField(blank=True, null=True )
    idle_start_time = models.DateTimeField(blank=True, null=True )
    idle_end_time = models.DateTimeField(blank=True, null=True )
    approved_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True, related_name='idle_time_approved_by')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True, related_name='idle_time_approval_user')






