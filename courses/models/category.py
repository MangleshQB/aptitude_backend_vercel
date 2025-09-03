from django.db import models
from utils.models import QBBaseModel


class Category(QBBaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
