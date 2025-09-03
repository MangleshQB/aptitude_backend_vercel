from django.contrib import admin
from .models import SalarySlip


@admin.register(SalarySlip)
class SalarySlipAdmin(admin.ModelAdmin):
    list_display = ['id']

