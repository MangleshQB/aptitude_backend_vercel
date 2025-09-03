from django.db import models
from app.models import CustomUser
from utils.models import QBBaseModel


class APIErrorLogs(QBBaseModel): #chnage name like APIErrorLogs
    method = models.CharField(null=True, blank=True, max_length=10)
    title = models.TextField(null=True, blank=True)
    trace = models.TextField(null=True, blank=True)
    path = models.URLField(null=True, blank=True)
    headers = models.TextField(null=True, blank=True)
    request_data = models.TextField(null=True, blank=True)
    response_data = models.TextField(null=True, blank=True)
    status_code = models.IntegerField(default=0)
    ip_address = models.CharField(null=True, blank=True, max_length=100)
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)