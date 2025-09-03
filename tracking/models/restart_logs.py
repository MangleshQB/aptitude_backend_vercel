from django.db import models

from app.models import CustomUser
from utils.models import QBBaseModel
import os


class RestartLogs(QBBaseModel):
    STARTED = "Started"
    RESTARTED = "Restarted"
    ENDED = "Ended"
    ERROR = "Error"

    TYPE_OF_STATUS = (
        (STARTED, "Started"),
        (RESTARTED, 'Restarted'),
        (ENDED, 'Ended'),
        (ERROR, 'Error'),
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    status = models.CharField(choices=TYPE_OF_STATUS, blank=True, null=True,max_length=255)
    description = models.TextField(blank=True, null=True)
