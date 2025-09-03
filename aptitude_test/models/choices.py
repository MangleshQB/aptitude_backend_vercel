from django.db import models

from utils.models import QBBaseModel


class Choices(QBBaseModel):
    name = models.CharField(max_length=500)
    is_correct = models.BooleanField()

    def __str__(self):
        return str(self.name)
