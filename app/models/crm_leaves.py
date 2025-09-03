from django.db import models
from .crm_users import Users
from .crm_leave_types import LeaveTypes

class Leaves(models.Model):
    user = models.ForeignKey(Users, models.DO_NOTHING)
    leave_type = models.ForeignKey(LeaveTypes, models.DO_NOTHING)
    duration = models.CharField(max_length=191)
    leave_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=8)
    reject_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    paid = models.IntegerField()
    added_by = models.ForeignKey(Users, models.DO_NOTHING, db_column='added_by', related_name='leaves_added_by_set', blank=True, null=True)
    last_updated_by = models.ForeignKey(Users, models.DO_NOTHING, db_column='last_updated_by', related_name='leaves_last_updated_by_set', blank=True, null=True)
    event_id = models.TextField(blank=True, null=True)
    approved_by = models.ForeignKey(Users, models.DO_NOTHING, db_column='approved_by', related_name='leaves_approved_by_set', blank=True, null=True)
    half_day_type = models.CharField(max_length=191, blank=True, null=True)
    approved_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'leaves'
        verbose_name = 'CRM Leaves'
        verbose_name_plural = 'CRM Leaves'

