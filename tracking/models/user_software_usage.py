from django.db import models

from app.models import CustomUser
from configuration.models import SoftwareProcess
from utils.models import QBBaseModel


class UserSoftwareUsage(QBBaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    software_process = models.ForeignKey(SoftwareProcess, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    total_usage = models.DecimalField(decimal_places=2, max_digits=255)
