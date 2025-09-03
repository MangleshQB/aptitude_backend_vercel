from django.db import models
from app.models.custom_user import CustomUser
from utils.models import QBBaseModel

class UserMouseTracking(QBBaseModel):

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    idle_time = models.DecimalField(max_digits=255, decimal_places=2)
    idle_start_time = models.DateTimeField()
    idle_end_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return str(self.id)

    class Meta:
        default_permissions = ["add", "change", "delete", "views", 'all', 'team', "owned"]

