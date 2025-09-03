import os

from django.contrib import admin

from tracking.models import UserMouseTracking, UserScreenshots, RestartLogs, EmployeeTimeSheet, UserSoftwareUsage, \
    IdleTimeApproval, IdleTimeApprovalReason, APIErrorLogs


# Register your models here.


@admin.register(UserMouseTracking)
class UserMouseTrackingAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'idle_time', 'idle_start_time', 'idle_end_time']
    list_filter = ['user']


class UserScreenshotsAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'file', 'created_at']

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            if obj.file and os.path.isfile(obj.file.path):
                os.remove(obj.file.path)
        super().delete_queryset(request, queryset)


@admin.register(RestartLogs)
class RestartLogsAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at']


admin.site.register(UserScreenshots, UserScreenshotsAdmin)


@admin.register(EmployeeTimeSheet)
class EmployeeTimeSheetAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'date', 'status']
    list_filter = ['date', 'user']


@admin.register(UserSoftwareUsage)
class UserSoftwareUsageAdmin(admin.ModelAdmin):
    list_display = ['id', 'start_time', 'end_time', 'total_usage']

@admin.register(IdleTimeApproval)
class IdleTimeApprovalAdmin(admin.ModelAdmin):
    list_display = ['id', 'idle_time','idle_start_time','idle_end_time','created_at']
    list_filter = ['user']


@admin.register(IdleTimeApprovalReason)
class IdleTimeApprovalReasonAdmin(admin.ModelAdmin):
    list_display = ['id','name']

@admin.register(APIErrorLogs)
class APIErrorLogsAdmin(admin.ModelAdmin):
    list_display = ['method','title','status_code','request_data']