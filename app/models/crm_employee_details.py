from django.db import models
from app.models.crm_users import Users
from app.models.crm_designations import Designations

class EmployeeDetails(models.Model):
    user = models.ForeignKey(Users, models.DO_NOTHING)
    employee_id = models.CharField(unique=True, max_length=191, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    hourly_rate = models.FloatField(blank=True, null=True)
    slack_username = models.CharField(unique=True, max_length=191, blank=True, null=True)
    # department = models.ForeignKey('Teams', models.DO_NOTHING, blank=True, null=True)
    designation = models.ForeignKey(Designations, models.DO_NOTHING, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    joining_date = models.DateTimeField()
    last_date = models.DateField(blank=True, null=True)
    added_by = models.ForeignKey(Users, models.DO_NOTHING, db_column='added_by', related_name='employeedetails_added_by_set', blank=True, null=True)
    last_updated_by = models.ForeignKey(Users, models.DO_NOTHING, db_column='last_updated_by', related_name='employeedetails_last_updated_by_set', blank=True, null=True)
    attendance_reminder = models.DateField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    calendar_view = models.TextField(blank=True, null=True)
    about_me = models.TextField(blank=True, null=True)
    reporting_to = models.ForeignKey(Users, models.DO_NOTHING, db_column='reporting_to', related_name='employeedetails_reporting_to_set', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'employee_details'
