from app.models import CustomUser
from utils.models import QBBaseModel
from django.db import models

class SalarySlip(QBBaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    hra = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0.0)
    conveyance_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, blank=True, null=True)
    medical_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, blank=True, null=True)
    provident_fund = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, blank=True, null=True)
    tds = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, blank=True, null=True)
    esic = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, blank=True, null=True)
    professional_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, blank=True, null=True)
    total_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, blank=True, null=True)
    marketing_expense = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, blank=True, null=True)
    statutory_bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, blank=True, null=True)
    other_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, blank=True, null=True)
    account_number = models.CharField(max_length=255, blank=True, null=True)
    bank_name = models.CharField(max_length=255, blank=True, null=True)
    ifsc_code = models.CharField(max_length=255, blank=True, null=True)
    loan_recovery = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, blank=True, null=True)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_earning = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_days = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    paid_days = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    designation = models.CharField(max_length=255, blank=True, null=True)
    department = models.CharField(max_length=255, blank=True, null=True)
    other_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, blank=True, null=True)
    pf_number = models.CharField(max_length=255, blank=True, null=True)
    esic_number = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateField()

    class Meta:
        default_permissions = ["add", "change", "delete", "view", 'all', "owned"]
