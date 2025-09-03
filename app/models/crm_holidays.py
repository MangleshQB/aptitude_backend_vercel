from django.db import models
from .crm_users import Users


class Holidays(models.Model):
    date = models.DateField()
    occassion = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    added_by = models.ForeignKey(Users, models.DO_NOTHING, db_column='added_by', blank=True, null=True)
    last_updated_by = models.ForeignKey(Users, models.DO_NOTHING, db_column='last_updated_by', related_name='holidays_last_updated_by_set', blank=True, null=True)
    event_id = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'holidays'
        verbose_name = 'CRM Holidays'
        verbose_name_plural = 'CRM Holidays'

