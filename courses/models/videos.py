from django.db import models
from app.models import CustomUser
from courses.models.category import Category
from utils.models import QBBaseModel


class Videos(QBBaseModel):
    title = models.CharField(max_length=255)
    duration = models.DurationField(blank=True, null=True)
    description = models.TextField()
    file = models.FileField(upload_to='course_videos/')
    order = models.PositiveIntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    thumbnail = models.ImageField(upload_to='video_thumbnail', blank=True, null=True)
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)
    # created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True,
    #                                related_name='video_created_by')
    # updated_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True,
    #                                related_name='video_updated_by')
    # deleted_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True,
    #                                related_name='video_deleted_by')
    # deleted_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title
