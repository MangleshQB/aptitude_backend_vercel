from django.db import models


class Designations(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=191)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    # added_by = models.ForeignKey('Users', models.DO_NOTHING, db_column='added_by', blank=True, null=True)
    # last_updated_by = models.ForeignKey('Users', models.DO_NOTHING, db_column='last_updated_by', related_name='designations_last_updated_by_set', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'designations'
