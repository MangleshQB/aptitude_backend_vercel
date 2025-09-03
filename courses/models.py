from django.db import models
from app.models import CustomUser








class Presenter(models.Model):
    name = models.CharField(max_length=255)
    designation = models.CharField(max_length=255)
    image = models.ImageField(upload_to='presenters/', blank=True, null=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True,
                                   related_name='presenter_created_by')
    updated_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True,
                                   related_name='presenter_updated_by')
    deleted_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True,
                                   related_name='presenter_deleted_by')
    deleted_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Videos(models.Model):
    title = models.CharField(max_length=255)
    duration = models.DurationField(blank=True, null=True)
    description = models.TextField()
    file = models.FileField(upload_to='course_videos/')
    order = models.PositiveIntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    thumbnail = models.ImageField(upload_to='video_thumbnail', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True,
                                   related_name='video_created_by')
    updated_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True,
                                   related_name='video_updated_by')
    deleted_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True,
                                   related_name='video_deleted_by')
    deleted_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title


class Courses(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    languages = models.ManyToManyField(Languages)
    topic = models.ManyToManyField(Topic)
    presenter = models.ForeignKey(Presenter, on_delete=models.CASCADE)
    videos = models.ManyToManyField(Videos)
    thumbnail = models.ImageField(upload_to='course_thumbnail', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    duration = models.DurationField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True,
                                   related_name='course_created_by')
    updated_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True,
                                   related_name='course_updated_by')
    deleted_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True,
                                   related_name='course_deleted_by')
    deleted_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title
