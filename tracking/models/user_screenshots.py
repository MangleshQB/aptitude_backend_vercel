from django.db import models
import datetime
from app.models.custom_user import CustomUser
from utils.models import QBBaseModel


def screenshots_file_name(instance, filename):
    date = datetime.datetime.now()
    return '/'.join(['screenshots', str(instance.user.id), str(date.year), str(date.month), str(date.day), filename])


class UserScreenshots(QBBaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    file = models.FileField(upload_to=screenshots_file_name)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        default_permissions = ["add", "change", "delete", "views", 'all', 'team', "owned"]
