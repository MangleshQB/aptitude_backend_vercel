from django.db import models
from app.models import CustomUser
from utils.models import QBBaseModel


class Topic(QBBaseModel):
    name = models.CharField(max_length=255)
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)
    # created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True,
    #                                related_name='course_topic_created_by')
    # updated_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True,
    #                                related_name='course_topic_updated_by')
    # deleted_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True,
    #                                related_name='course_topic_deleted_by')
    # deleted_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.name
