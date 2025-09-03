from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, PermissionsMixin, BaseUserManager
from django.contrib.contenttypes.models import ContentType
from django.db import models
from app.models import Designation


class UserAccountManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email')
        # email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(user.password)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email')
        # email = self.normalize_email(email)
        superuser = self.model(email=email, **extra_fields)
        superuser.set_password(password)
        superuser.is_superuser = True
        superuser.is_staff = True
        superuser.save()
        return superuser

class CustomUser(AbstractUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True, null=True, blank=True)
    designation = models.ForeignKey(Designation, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(unique=True, max_length=255, null=True, blank=True)
    password = models.CharField(max_length=300)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_superuser = models.BooleanField(default=False)
    joining_date = models.DateField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    anniversary = models.DateField(null=True, blank=True)
    is_using_surveillance_software = models.BooleanField(default=False)
    objects = UserAccountManager()
    employee_id = models.CharField(blank=True, null=True,max_length=255)
    is_surveillance_active = models.BooleanField(default=True)
    is_screenshot_active = models.BooleanField(default=False)
    reporting_to = models.ForeignKey('self', blank=True, null=True, on_delete=models.SET_NULL, related_name='subordinates', related_query_name='subordinates')
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    is_probation = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "User"
        default_permissions = ["add", "change", "delete", "view", 'all', 'team', "owned"]

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        super(CustomUser, self).save(*args, **kwargs)