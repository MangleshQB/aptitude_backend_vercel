from django.db import models
from django.contrib.contenttypes.models import ContentType
from utils.models import QBBaseModel


class AllowedContentType(models.Model):
    content_type = models.OneToOneField(ContentType, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.content_type)

