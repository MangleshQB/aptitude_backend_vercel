import pandas as pd
from io import BytesIO
from django.core.validators import FileExtensionValidator
from django.db import transaction
import numpy as np
from xlsxwriter.contenttypes import defaults

from app.models import CustomUser
from .models import SalarySlip
from rest_framework import serializers
from utils.serializer import BaseModelSerializerCore, RelatedFieldAlternative, RefUserSerializer


class SalarySlipSerializer(BaseModelSerializerCore):
    user = RelatedFieldAlternative(queryset = CustomUser.objects.all(),serializer=RefUserSerializer)

    class Meta:
        model = SalarySlip
        fields = '__all__'
        write_only = [
            'basic_salary',
            'hra',
            'uniform_allowance',
            'project_incentive',
            'medical_allowance',
            'provident_fund',
            'tds',
            'esic',
            'professional_tax',
            'total_deducation',
            'gross_salary',
            'statutory_bonus',
            'net_salary_take_home',
            'total_earning_a',
            'pf_contribution_employer',
            'esic_contribution_employer',
            'total_b',
            'total_deduction',
            'monthly',
            'axis_bank_acc_number',
            'bank_name',
            'ifsc_code',
        ]

class SalarySlipUploadSerializer(serializers.Serializer):
    file = serializers.FileField(validators=[FileExtensionValidator(allowed_extensions=['xlsx'])])
    date = serializers.DateField(write_only=True)
    not_found_ids = serializers.ListField(read_only=True)

    @transaction.atomic
    def create(self, validated_data):
        file = validated_data['file']
        date = validated_data['date']

        old = SalarySlip.objects.filter(date=date)
        print(old)

        file_content = file.read()
        df = pd.read_excel(BytesIO(file_content), sheet_name='Sheet1')
        # print(df.columns.tolist())
        # for i in df.columns.tolist():
        #     print(i)
        df = df.applymap(lambda x: None if x == '' or x == '-' or str(x) == 'nan' else x)

        not_found_ids = []

        # salary_slip = None
        for index, row in df.iterrows():
            ctx={}
            id = f"QB{int(row['Employee ID'].replace('QB', '')):03}"
            user = CustomUser.objects.filter(employee_id=id).first()
            print('Marketing Expense (Reimbursement)',row.get('Marketing Expense (Reimbursement)', 0.0))

            if not user:

                print(f"User with employee_id {id} not found.")
                ctx['name'] = row.get('Name of Employee ', '')
                ctx['employee_id'] = id
                not_found_ids.append(ctx)
                continue
            defaults = {
                'basic_salary': row.get('Basic Salary', 0.0),
                'hra': row.get('HRA', 0.0),
                'conveyance_allowance': row.get('Conveyance Allowance', 0.0),
                'medical_allowance': row.get('Medical Allowance', 0.0),
                'provident_fund': row.get('Provident Fund', 0.0),
                'tds': row.get('TDS', 0.0),
                'esic': row.get('ESIC', 0.0),
                'professional_tax': row.get('Professional Tax', 0.0),
                'total_deduction': row.get('Total Deduction', 0.0),
                'marketing_expense': row.get('Marketing Expense (Reimbursement)', 0.0),
                'statutory_bonus': row.get('Statutory Bonus', 0.0),
                'other_deduction': row.get('Other Deduction', 0.0),
                'account_number': row.get('Axis Bank Acc. Number', ''),
                'bank_name': row.get('Bank Name', ''),
                'ifsc_code': str(row.get('IFSC Code', '')),
                'loan_recovery': row.get('Loan Recovery', 0.0),
                'net_salary': row.get('Net Salary', 0.0),
                # 'total_earning' : row.get('total earning', None),
                'total_days': row.get('Total Days', 0),
                'designation': row.get('Designation', ''),
                'department': row.get('Department', ''),
                'paid_days': row.get('Paid Days', 0),
                'other_allowance': row.get('Other Allowance', 0.0),
                'pf_number': row.get('PF Number', ''),
                'esic_number': row.get('ESIC Number', ''),
            }


            salary_slip = SalarySlip.objects.update_or_create(
                user= user,
                date= date,
                defaults=defaults
            )

        return {'date':date, 'file':file, 'not_found_ids': not_found_ids}




#[ 'Statutory Bonus', 'other deduction', 'Axis Bank Acc. Number', 'Bank Name', 'IFSC Code', 'Loan Recovery', 'Net Salary', 'Designation', 'Department', 'total day']















