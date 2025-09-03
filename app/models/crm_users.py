from django.db import models


class Users(models.Model):
    name = models.CharField(max_length=191)
    email = models.CharField(unique=True, max_length=191, blank=True, null=True)
    password = models.CharField(max_length=191)
    two_factor_secret = models.TextField(blank=True, null=True)
    two_factor_recovery_codes = models.TextField(blank=True, null=True)
    two_factor_confirmed = models.IntegerField()
    two_factor_email_confirmed = models.IntegerField()
    remember_token = models.CharField(max_length=100, blank=True, null=True)
    image = models.CharField(max_length=191, blank=True, null=True)
    mobile = models.CharField(max_length=191, blank=True, null=True)
    gender = models.CharField(max_length=6, blank=True, null=True)
    salutation = models.CharField(max_length=5, blank=True, null=True)
    locale = models.CharField(max_length=191)
    status = models.CharField(max_length=8)
    login = models.CharField(max_length=7)
    onesignal_player_id = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    last_login = models.DateTimeField(blank=True, null=True)
    email_notifications = models.IntegerField()
    dark_theme = models.IntegerField()
    rtl = models.IntegerField()
    two_fa_verify_via = models.CharField(max_length=20, blank=True, null=True)
    two_factor_code = models.CharField(max_length=191, blank=True, null=True, db_comment='when authenticator is email')
    two_factor_expires_at = models.DateTimeField(blank=True, null=True)
    admin_approval = models.IntegerField()
    permission_sync = models.IntegerField()
    google_calendar_status = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'users'
        # indexes = [
        #     models.Index(fields=['email'], name='idx_users_email'),
        # ]