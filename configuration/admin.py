from django.contrib import admin
from .models import SoftwareConfiguration, App_Version, SoftwareProcess, Holiday, LeaveTypes, LeaveBalance, \
    TicketCategory, TicketSubCategory, UserAppVersion
import os


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']



@admin.register(SoftwareConfiguration)
class SoftwareConfigurationAdmin(admin.ModelAdmin):
    list_display = ['id']

@admin.register(App_Version)
class AppVersionAdmin(admin.ModelAdmin):
    list_display = ['id', 'version']

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            if obj.exe and os.path.isfile(obj.exe.path):
                os.remove(obj.exe.path)
        super().delete_queryset(request, queryset)


@admin.register(SoftwareProcess)
class SoftwareProcessAdmin(admin.ModelAdmin):
    list_display = ['id', 'display_name', 'icon', 'os_type']

@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ['id', 'balance', 'total']

@admin.register(LeaveTypes)
class LeaveTypesAdmin(admin.ModelAdmin):
    list_display = ['id', "type","limit","start_range","end_range","el_after","lc_before","wfh_start_time","wfh_end_time","fh_hours","sh_hours"]





@admin.register(TicketCategory)
class TicketCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    filter_horizontal = ('notify_to',)

@admin.register(TicketSubCategory)
class TicketSubCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


@admin.register(UserAppVersion)
class UserAppVersionAdmin(admin.ModelAdmin):
    list_display = ['id','user','version']