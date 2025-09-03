from django.db import models
from app.models import Designation
from utils.models import QBBaseModel


class Configuration(QBBaseModel):
    designation = models.OneToOneField(Designation, on_delete=models.CASCADE)
    no_questions_to_asked = models.IntegerField(blank=True, null=True)
    time_limit = models.IntegerField(blank=True, null=True)
    office_start = models.TimeField(blank=True, null=True)
    office_end = models.TimeField(blank=True, null=True)
