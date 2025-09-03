from utils.models import QBBaseModel
from django.db import models

class Holiday(QBBaseModel):
    half_day = 1
    full_day = 2

    LEAVE_TYPE_CHOICES = (
        (half_day, "Half Day"),
        (full_day, "Full Day"),
    )

    name = models.CharField(max_length=255)
    date = models.DateField()
    description = models.TextField(blank=True, null=True)
    type = models.PositiveSmallIntegerField(choices=LEAVE_TYPE_CHOICES, default=full_day)
    repeats_annually = models.BooleanField(default=False)

    def __str__(self):
        return self.name