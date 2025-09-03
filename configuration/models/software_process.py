from django.db import models
from utils.models import QBBaseModel


class SoftwareProcess(QBBaseModel):
    display_name = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    icon = models.ImageField(upload_to='software_icon/')

    Window = "Window"
    Linux = "Linux"
    Mac = "Mac"

    TYPE_OF_OS = (
        (Window, "Window"),
        (Linux, 'Linux'),
        (Mac, 'Mac'),
    )

    os_type = models.CharField(choices=TYPE_OF_OS, max_length=255, default=Window)

    def __str__(self):
        return self.display_name