from django.contrib.contenttypes.models import ContentType
from django.db import models

from utils.models import QBBaseModel


class SoftwareConfiguration(QBBaseModel):
    ss_duration = models.FloatField()
    mouse_duration = models.FloatField()
    idle_time_concern_hours_limit = models.FloatField(default=24.0)
    
    def __str__(self):
        return str(self.id)


