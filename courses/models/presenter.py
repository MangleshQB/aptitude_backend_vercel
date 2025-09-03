from django.db import models
from app.models import CustomUser
from utils.models import QBBaseModel


class Presenter(QBBaseModel):
    name = models.CharField(max_length=255)
    designation = models.CharField(max_length=255)
    image = models.ImageField(upload_to='presenters/', blank=True, null=True)
    # created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True,
    #                                related_name='presenter_created_by')
    # updated_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True,
    #                                related_name='presenter_updated_by')
    # deleted_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True,
    #                                related_name='presenter_deleted_by')
    # deleted_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.name
    