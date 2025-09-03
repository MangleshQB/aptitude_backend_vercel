from django.db import models
from utils.models import QBBaseModel
import os


def exe_file_name(instance, filename):
    ext = os.path.splitext(filename)[1]
    new_filename = f"{os.path.splitext(filename)[0]}_{instance.version}{ext}"
    return '/'.join(['exe', new_filename])


class App_Version(QBBaseModel):
    windows_os = "Windows"
    linux_os = "Linux"
    mac_os = "Mac"

    choices = (
        (windows_os, "Windows"),
        (linux_os, "Linux"),
        (mac_os, "Mac"),
    )
    system_os = models.CharField(choices = choices, default = windows_os, max_length = 120)
    version = models.CharField(max_length=100, null=True, blank=True)
    exe = models.FileField(upload_to=exe_file_name)
    description = models.TextField(blank=True, null=True)


    def __str__(self):
        return str(self.id)

    def delete(self, *args, **kwargs):
        if self.exe and os.path.isfile(self.exe.path):
            os.remove(self.exe.path)
        super().delete(*args, **kwargs)