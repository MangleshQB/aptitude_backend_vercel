from django.db import models


class LeaveTypes(models.Model):
    type_name = models.CharField(max_length=191)
    color = models.CharField(max_length=191)
    no_of_leaves = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    paid = models.IntegerField()
    monthly_limit = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'leave_types'
        verbose_name = 'CRM Leave Type'
        verbose_name_plural = 'CRM Leave Type'