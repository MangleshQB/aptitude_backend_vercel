from django.contrib import admin
from django.contrib.admin import DateFieldListFilter
from django.contrib.auth.hashers import make_password
from .models.crm_users import Users as CRMUser
from .models import CustomUser, Designation, AllowedContentType, IclockTransaction, PersonnelEmployee, Leaves, \
    LeaveTypes, Holidays
from import_export.admin import ImportExportModelAdmin


@admin.register(CustomUser)
class CustomUserAdmin(ImportExportModelAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'designation', 'employee_id', 'is_screenshot_active')
    search_fields = ('first_name', 'last_name')

    def save_model(self, request, obj, form, change):
        if obj.password and not obj.password.startswith(('pbkdf2_sha256$', 'bcrypt$', 'argon2')):
            obj.password = make_password(obj.password)
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.exclude(username='manglesh@gmail.com')

@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = (['id', 'name'])

@admin.register(Holidays)
class HolidaysAdmin(admin.ModelAdmin):
    list_display = ['id', 'date', 'occassion']
    using = 'crm'

    def save_model(self, request, obj, form, change):
        obj.save(using=self.using)

    def delete_model(self, request, obj):
        obj.delete(using=self.using)

    def get_queryset(self, request):
        return super().get_queryset(request).using(self.using)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        return super().formfield_for_foreignkey(
            db_field, request, using=self.using, **kwargs
        )

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        return super().formfield_for_manytomany(
            db_field, request, using=self.using, **kwargs
        )


@admin.register(IclockTransaction)
class IclockTransactionAdmin(admin.ModelAdmin):
    list_display = ['emp_code', 'punch_time', 'punch_state']
    search_fields = ['emp_code']
    list_filter = [('punch_time', DateFieldListFilter), 'emp_code']
    using = 'zkteco'

    def save_model(self, request, obj, form, change):
        obj.save(using=self.using)

    def delete_model(self, request, obj):
        obj.delete(using=self.using)

    def get_queryset(self, request):
        return super().get_queryset(request).using(self.using)

    # .filter(emp_code__iexact=6)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        return super().formfield_for_foreignkey(
            db_field, request, using=self.using, **kwargs
        )

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        return super().formfield_for_manytomany(
            db_field, request, using=self.using, **kwargs
        )


@admin.register(PersonnelEmployee)
class PersonnelEmployeeAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name']
    using = 'zkteco'

    def save_model(self, request, obj, form, change):
        obj.save(using=self.using)

    def delete_model(self, request, obj):
        obj.delete(using=self.using)

    def get_queryset(self, request):
        return super().get_queryset(request).using(self.using)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        return super().formfield_for_foreignkey(
            db_field, request, using=self.using, **kwargs
        )

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        return super().formfield_for_manytomany(
            db_field, request, using=self.using, **kwargs
        )


@admin.register(AllowedContentType)
class AllowedContentTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'content_type', 'is_active']


@admin.register(Leaves)
class LeavesAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        # 'user__email',
        'duration',
        'leave_date',
        'reason',
        'status',
        'reject_reason',
        'created_at',
        'updated_at',
        'paid',
        'added_by',
        'event_id',
        'approved_by',
        'half_day_type',
        'approved_at',
    )
    using = 'crm'

    def save_model(self, request, obj, form, change):
        obj.save(using=self.using)

    def delete_model(self, request, obj):
        obj.delete(using=self.using)

    def get_queryset(self, request):
        return super().get_queryset(request).using(self.using)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        return super().formfield_for_foreignkey(
            db_field, request, using=self.using, **kwargs
        )

@admin.register(LeaveTypes)
class LeaveTypesAdmin(admin.ModelAdmin):
    list_display = (
        'type_name',
        'color',
        'no_of_leaves',
        'created_at',
        'updated_at',
        'paid',
        'monthly_limit',
    )
    using = 'crm'


    def save_model(self, request, obj, form, change):
        obj.save(using=self.using)

    def delete_model(self, request, obj):
        obj.delete(using=self.using)

    def get_queryset(self, request):
        return super().get_queryset(request).using(self.using)