from django.db import models
from utils.models import QBBaseModel
from app.models import CustomUser
from .leave_types import LeaveTypes

class LeaveBalance(QBBaseModel):
    leave_type = models.ForeignKey(LeaveTypes, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    total = models.PositiveIntegerField(default=0)

    def __str__(self):
        return str(self.user.email)

    class Meta:
        default_permissions = ["add", "change", "delete", "views", 'all', 'team', "owned"]

