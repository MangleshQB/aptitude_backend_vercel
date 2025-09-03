from django.contrib import admin

from hrms.models import Ticket, Leave
from hrms.models.knowledge_base import KnowledgeBase, KnowledgeBaseCategory, KnowledgeBaseFile


# Register your models here.
@admin.register(Ticket)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'category', 'sub_category', 'is_deleted']
    filter_horizontal = ('notify_to',)

@admin.register(KnowledgeBase)
class KnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ['id', 'title']

@admin.register(KnowledgeBaseCategory)
class KnowledgeBaseCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


@admin.register(KnowledgeBaseFile)
class KnowledgeBaseFileAdmin(admin.ModelAdmin):
    list_display = ["file"]

@admin.register(Leave)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ['id', 'description', 'user', 'leave_type', 'is_deleted']