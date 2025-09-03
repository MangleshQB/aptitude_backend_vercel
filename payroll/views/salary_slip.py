import pdfkit
from django.conf import settings
from django.http import HttpResponse
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from decimal import Decimal
from configuration.models import Holiday
from payroll.models import SalarySlip
from payroll.serializer import SalarySlipSerializer, SalarySlipUploadSerializer
from tracking.models import EmployeeTimeSheet
from utils.views import CustomModelViewSet
from django.template.loader import render_to_string, get_template


# Ensure WKHTMLTOPDF_PATH is correct
WKHTMLTOPDF_PATH = settings.WKHTMLTOPDF_PATH

# On Linux, use the following:
# WKHTMLTOPDF_PATH = '/usr/local/bin/wkhtmltopdf'

import calendar
from datetime import date, timedelta

def calculate_working_days(year, month):
    holidays = Holiday.objects.all().values_list('date')
    first_day, last_day = date(year, month, 1), date(year, month, calendar.monthrange(year, month)[1])

    working_days = 0
    current_day = first_day
    while current_day <= last_day:
        if current_day.weekday() < 5 and current_day not in holidays:  # Monday=0, Sunday=6
            working_days += 1
        current_day += timedelta(days=1)

    return working_days

# todo: Render To PDF Salary Slip (for salary_slip.html)
def render_to_pdf_salary_slip(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    options = {
        'page-size': 'A4',
        'page-height': "11.7in",
        'page-width': "8.3in",
        'margin-top': '0in',
        'margin-right': '0in',
        'margin-left': '0in',
        'encoding': "UTF-8",
        'no-outline': None,
        'margin-bottom': '0.50in',
        'footer-right': 'Total [page] of [topage]',
        'header-right': 'Your Static Header Text',
    }
    config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)
    pdf = pdfkit.from_string(html, False, configuration=config, options=options)
    # Serve as HTTP response
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="salary_slip.pdf"'
    return response


# todo: file uploaded and payslip download
class SalarySlipViewSet(CustomModelViewSet):
    queryset = SalarySlip.objects.filter(is_deleted=False).order_by('-id')
    permission_classes = [IsAuthenticated]
    serializer_class = SalarySlipSerializer

    def create(self, request, *args, **kwargs):
        serializer = SalarySlipUploadSerializer(data=request.data,context={'created_by': request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        not_found_id = serializer.data.get('not_found_ids',[])
        self.response_format["data"] = 'file uploaded successfully'
        self.response_format['not_found_data'] = not_found_id
        self.response_format["status"] = True
        return Response(self.response_format, status=status.HTTP_200_OK)


    def update(self, request, *args, **kwargs):

        data = request.data
        data['total_earning'] = (Decimal(data.get('basic_salary', 0.0) if data.get('basic_salary', 0.0) else 0.0) + Decimal(data.get('hra', 0.0) if data.get('hra', 0.0) else 0.0) + Decimal(data.get('conveyance_allowance', 0.0) if data.get('conveyance_allowance', 0.0) else 0.0) + Decimal(data.get('medical_allowance', 0.0) if data.get('medical_allowance', 0.0) else 0.0) + Decimal(data.get('statutory_bonus', 0.0) if data.get('statutory_bonus', 0.0) else 0.0) + Decimal(data.get('other_allowance', 0.0) if data.get('other_allowance', 0.0) else 0.0) + Decimal(data.get('marketing_expense', 0.0) if data.get('marketing_expense', 0.0) else 0.0) + Decimal(data.get('net_salary', 0.0) if data.get('net_salary', 0.0) else 0.0))
        print(data['total_earning'])
        data['total_deduction'] = (Decimal(data.get('provident_fund', 0.0) if data.get('provident_fund', 0.0) else 0.0) + Decimal(data.get('esic', 0.0) if data.get('esic', 0.0) else 0.0) + Decimal(data.get('professional_tax', 0.0) if data.get('professional_tax', 0.0) else 0.0) + Decimal(data.get('loan_recovery', 0.0) if data.get('loan_recovery', 0.0) else 0.0) + Decimal(data.get('other_deduction', 0.0) if data.get('other_deduction', 0.0) else 0.0))
        print(data['total_deduction'])


        obj = self.get_object()
        serializer = self.serializer_class(instance=obj, data=request.data, context={'updated_by': request.user},
                                           partial=True)
        if serializer.is_valid():
            serializer.save()
            self.response_format["data"] = serializer.data
            self.response_format["status"] = True
            return Response(self.response_format, status=status.HTTP_200_OK)
        else:
            self.response_format["data"] = serializer.errors
            self.response_format["status"] = False
            self.response_format["error"] = status.HTTP_400_BAD_REQUEST
            self.response_format["message"] = "Validation failed"
            return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):

        permissions = request.user.groups.all().first().permissions.filter(
            content_type__model='salaryslip').values_list('codename', flat=True)

        base_permissions = [permission.split('_')[0] for permission in permissions]

        if 'all' in base_permissions:
            self.queryset = SalarySlip.objects.filter(is_deleted=False).order_by('-id')

        elif 'owned' in base_permissions:
            self.queryset = SalarySlip.objects.filter(user=request.user,is_deleted=False).order_by('-id')
        else:
            self.response_format["status"] = False
            self.response_format["message"] = "User have not permission"
            return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)




        if request.GET.get("search", None) or request.GET.get("ordering", None):
            queryset = self.filter_queryset(self.get_queryset())
        else:
            queryset = self.get_queryset()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)

            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        self.response_format["data"] = serializer.data
        self.response_format["status"] = True
        if not serializer.data:
            self.response_format["message"] = "No data found!"
        return Response(self.response_format, status=status.HTTP_200_OK)

    @action(detail=True, methods=["GET"], url_path="download_payslip", name="payslip")
    def download_payslip(self, request,pk=None):
        permissions = request.user.groups.all().first().permissions.filter(
            content_type__model='salaryslip').values_list('codename', flat=True)

        base_permissions = [permission.split('_')[0] for permission in permissions]

        salary_slip = self.get_object()

        if 'all' in base_permissions:
            pass
        elif 'owned' in base_permissions:
            if not salary_slip.user == request.user:
                self.response_format["status"] = False
                self.response_format["message"] = "User have not permission"
                return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)
        else:
            self.response_format["status"] = False
            self.response_format["message"] = "User have not permission"
            return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)



        # emp = salary_slip.user
        # print(emp)
        # calculate_paid_days = EmployeeTimeSheet.objects.filter(date__year = salary_slip.date.year,date__month = salary_slip.date.month,user = salary_slip.user).count()
        total_earning = (Decimal(salary_slip.basic_salary if salary_slip.basic_salary else 0.0) + Decimal(salary_slip.hra if salary_slip.hra else 0.0) + Decimal(salary_slip.conveyance_allowance if salary_slip.conveyance_allowance else 0.0) + Decimal(salary_slip.medical_allowance if salary_slip.medical_allowance else 0.0) + Decimal(salary_slip.statutory_bonus if salary_slip.statutory_bonus else 0.0) + Decimal(salary_slip.other_allowance if salary_slip.other_allowance else 0.0) + Decimal(salary_slip.marketing_expense if salary_slip.marketing_expense else 0.0) + Decimal(salary_slip.net_salary if salary_slip.net_salary else 0.0))
        print(total_earning)
        total_deduction = (Decimal(salary_slip.provident_fund if salary_slip.provident_fund else 0.0) + Decimal(salary_slip.esic if salary_slip.esic else 0.0) + Decimal(salary_slip.professional_tax if salary_slip.professional_tax else 0.0) + Decimal(salary_slip.loan_recovery if salary_slip.loan_recovery else 0.0) + Decimal(salary_slip.other_deduction if salary_slip.other_deduction else 0.0))
        print(total_deduction)
        if not salary_slip:
            return Response({"e": "Payslip not found"}, status=404)

        context = {
            "user": salary_slip.user,
            "employee_id": salary_slip.user.employee_id if salary_slip.user.employee_id else '-',
            "conveyance_allowance": salary_slip.conveyance_allowance if salary_slip.conveyance_allowance else 0.0,
            "marketing_expense": salary_slip.marketing_expense if salary_slip.marketing_expense else 0.0,
            "basic_salary": salary_slip.basic_salary if salary_slip.basic_salary else 0.0,
            "hra": salary_slip.hra if salary_slip.hra else 0.0,
            "department": salary_slip.department if salary_slip.department else '-',
            "medical_allowance": salary_slip.medical_allowance if salary_slip.medical_allowance else 0.0,
            "provident_fund_number": salary_slip.pf_number if salary_slip.pf_number else '-',
            "provident_fund": salary_slip.provident_fund if salary_slip.provident_fund else 0.0,
            "tds": salary_slip.tds if salary_slip.tds else 0.0,
            "esic_deduction": salary_slip.esic if salary_slip.esic else 0.0,
            "esic_number": salary_slip.esic_number if salary_slip.esic_number else '-',
            "professional_tax": salary_slip.professional_tax if salary_slip.professional_tax else 0.0,
            "statutory_bonus": salary_slip.statutory_bonus if salary_slip.statutory_bonus else 0.0,
            "net_salary": salary_slip.net_salary if salary_slip.net_salary else 0.0,
            "total_deduction": total_deduction if total_deduction else 0.0,
            "account_number": salary_slip.account_number if salary_slip.account_number else '-',
            "other_deduction": salary_slip.other_deduction if salary_slip.other_deduction else 0.0,
            "other_allowance": salary_slip.other_allowance if salary_slip.other_allowance else 0.0,
            "loan_recovery": salary_slip.loan_recovery if salary_slip.loan_recovery else 0.0,
            "bank_name": salary_slip.bank_name if salary_slip.bank_name else '-',
            "ifsc_code": salary_slip.ifsc_code if salary_slip.ifsc_code else '-',
            "date": salary_slip.date if salary_slip.date else '-',
            "total_days": calculate_working_days(salary_slip.date.year, salary_slip.date.month),
            "paid_days": salary_slip.paid_days if salary_slip.paid_days else 0,
            "total_earning": total_earning if total_earning else 0.0,
        }
        return render_to_pdf_salary_slip('salary_slip.html', context)





# ['Sr No', 'Name of Employee :', 'Joining Date', 'Basic Salary', 'HRA', 'Uniform Allowance', 'Project Incentive', 'Medical Allowance', 'Provident Fund', 'TDS', 'ESIC', 'Professional Tax', 'Total Deducation', 'Gorss Salary', 'Statutory Bonus', 'Net Salary (Take Home)', 'Total Earning - A', 'PF Contribution Employer', 'ESIC Contribution Employer', 'Total B', 'Total Deduction', 'Monthly', 'Axis Bank Acc. Number', 'Bank Name', 'IFSC Code']

