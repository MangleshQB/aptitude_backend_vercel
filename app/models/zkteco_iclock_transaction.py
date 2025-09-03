from django.db import models

from .zkteco_personnel_employee import PersonnelEmployee


class IclockTransaction(models.Model):
    emp_code = models.CharField(max_length=20)
    punch_time = models.DateTimeField()
    punch_state = models.CharField(max_length=5)
    verify_type = models.IntegerField()
    work_code = models.CharField(max_length=20, blank=True, null=True)
    terminal_sn = models.CharField(max_length=50, blank=True, null=True)
    terminal_alias = models.CharField(max_length=50, blank=True, null=True)
    area_alias = models.CharField(max_length=120, blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    gps_location = models.TextField(blank=True, null=True)
    mobile = models.CharField(max_length=50, blank=True, null=True)
    source = models.SmallIntegerField(blank=True, null=True)
    purpose = models.SmallIntegerField(blank=True, null=True)
    crc = models.CharField(max_length=100, blank=True, null=True)
    is_attendance = models.SmallIntegerField(blank=True, null=True)
    reserved = models.CharField(max_length=100, blank=True, null=True)
    upload_time = models.DateTimeField(blank=True, null=True)
    sync_status = models.SmallIntegerField(blank=True, null=True)
    sync_time = models.DateTimeField(blank=True, null=True)
    emp = models.ForeignKey(PersonnelEmployee, models.DO_NOTHING, blank=True, null=True)
    # terminal = models.ForeignKey('IclockTerminal', models.DO_NOTHING, blank=True, null=True)
    # company = models.ForeignKey('PersonnelCompany', models.DO_NOTHING, blank=True, null=True)
    mask_flag = models.IntegerField(blank=True, null=True)
    temperature = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'iclock_transaction'
        unique_together = (('emp_code', 'punch_time', 'terminal_sn'),)
