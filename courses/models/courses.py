from django.db import models
from app.models import CustomUser
from courses.models.languages import Languages
from courses.models.presenter import Presenter
from courses.models.topic import Topic
from courses.models.videos import Videos
from utils.models import QBBaseModel


class Courses(QBBaseModel):
    title = models.CharField(max_length=255)
    description = models.TextField()
    languages = models.ManyToManyField(Languages)
    topic = models.ManyToManyField(Topic)
    presenter = models.ForeignKey(Presenter, on_delete=models.CASCADE)
    videos = models.ManyToManyField(Videos)
    thumbnail = models.ImageField(upload_to='course_thumbnail', blank=True, null=True)
    # created_at = models.DateTimeField(auto_now_add=True)
    duration = models.DurationField(blank=True, null=True)
    # updated_at = models.DateTimeField(auto_now=True)
    # created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True,
    #                                related_name='course_created_by')
    # updated_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True,
    #                                related_name='course_updated_by')
    # deleted_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True,
    #                                related_name='course_deleted_by')
    # deleted_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title
