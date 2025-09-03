from django.db import models

from app.models import CustomUser
from utils.models import QBBaseModel

class UserAppVersion(QBBaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    version = models.CharField(max_length=255, blank=True, null=True)