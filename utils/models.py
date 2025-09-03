from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import models

user = get_user_model()

class QBBaseModel(models.Model):

    class Meta:
        abstract = True

    created_by = models.ForeignKey(
        user,
        on_delete=models.SET_NULL,
        related_name='%(app_label)s_%(class)s_created_by',
        blank=True,
        null=True,
    )
    updated_by = models.ForeignKey(
        user,
        on_delete=models.SET_NULL,
        related_name='%(app_label)s_%(class)s_updated_by',
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    deleted_by = models.ForeignKey(
        user,
        on_delete=models.SET_NULL,
        related_name='%(app_label)s_%(class)s_deleted_by',
        blank=True,
        null=True,
    )

    deleted_at = models.DateTimeField(blank=True, null=True)

    def check_exist(self, request):
        return True

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        self.is_deleted = False
        self.save()
