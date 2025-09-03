import pytz
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import datetime, timedelta
from utils.common import ResponseFormat
from django.utils import timezone
from django.http import JsonResponse
from app.models import CustomUser, PersonnelEmployee, IclockTransaction
from tracking.models import UserMouseTracking
from django.db.models import Sum


class PunchLogs(APIView):
    permission_classes = [IsAuthenticated]
    def __init__(self, **kwargs):
        self.response_format = ResponseFormat().response
        super().__init__(**kwargs)

    def get(self, request, *args, **kwargs):
        date = request.GET.get('date', None)
        email = request.GET.get('email', None)

        if date and email:
            try:
                try:
                    start_date = timezone.make_aware(datetime.strptime(date, "%d/%m/%Y"), timezone=pytz.UTC)
                except:
                    raise ValueError('Wrong date format, Valid format is DD/MM/YYYY')

                user = CustomUser.objects.filter(email=email).first()
                if not user:raise ValueError('user not found!')

                try:
                    employee_id = int(str(user.employee_id).replace('QB', ''))
                except:
                    raise ValueError('employee id not found!')

                try:
                    zkteco_user = PersonnelEmployee.objects.using('zkteco').get(emp_code=employee_id)
                except:
                    raise ValueError('zkteco user not found!')

                IclockTransaction_use = list(IclockTransaction.objects.using('zkteco').filter(
                    emp=zkteco_user,
                    punch_time__gte=start_date,
                    punch_time__lte=start_date + timedelta(days=1),
                ).values('punch_time', 'punch_state'))

                if not IclockTransaction_use:
                    raise ValueError('punch transaction not found!')

                all_logs = [{'punch_state':i['punch_state'], 'punch_time':i['punch_time'].strftime("%Y-%m-%d %H:%M:%S")} for i in list(IclockTransaction_use)]

                self.response_format['status'] = True
                self.response_format['data'] = all_logs
                return Response(self.response_format, status=status.HTTP_200_OK)

            except Exception as e:
                self.response_format['error'] = str(e)
                self.response_format['status'] = False
                return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)

        self.response_format['error'] = 'missing date or email'
        self.response_format['status'] = False
        self.response_format['data'] = []
        return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)




