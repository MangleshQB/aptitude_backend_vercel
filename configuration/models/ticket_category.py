from django.db import models

from app.models import CustomUser
from utils.models import QBBaseModel

class TicketCategory(QBBaseModel):
    name = models.CharField(max_length=255)
    notify_to = models.ManyToManyField(CustomUser)

    def __str__(self):
        return self.name