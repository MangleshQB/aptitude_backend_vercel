from django.db.models import F
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import date
from app.models import CustomUser
from configuration.models import Holiday
from utils.common import ResponseFormat
from operator import itemgetter


class UpcomingEmployeesBirthday(APIView):

    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        self.response_format = ResponseFormat().response
        super().__init__(**kwargs)

    def get(self, request, *args, **kwargs):

        birthday_list = list(
            CustomUser.objects.filter(
                date_of_birth__month=date.today().month,
                date_of_birth__day__gte=date.today().day).annotate(designation_name=F('designation__name'))
            .values('first_name','last_name', 'designation_name','date_of_birth').order_by('date_of_birth'))

        if birthday_list:
            for data in birthday_list:
                data['in_days'] = int(data['date_of_birth'].day)-int(date.today().day)
            # print(birthday_list)

            birthday_list = sorted(birthday_list, key=itemgetter('in_days'))

            self.response_format['status'] = True
            self.response_format['data'] = birthday_list
            return Response(self.response_format, status=status.HTTP_200_OK)

        self.response_format['status'] = True
        self.response_format['data'] = 'there is no birthday of employees in this month'
        return Response(self.response_format, status=status.HTTP_200_OK)


class UpcomingEmployeesWorkAnniversary(APIView):

    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        self.response_format = ResponseFormat().response
        super().__init__(**kwargs)

    def get(self, request, *args, **kwargs):


        anniversary_list = list(
            CustomUser.objects.filter(
                joining_date__month=date.today().month,
                joining_date__day__gte=date.today().day)
            .exclude(joining_date=date.today())
            .annotate(designation_name=F('designation__name'))
            .values('first_name','last_name', 'designation_name', 'joining_date').order_by('joining_date'))

        if anniversary_list:
            for data in anniversary_list:
                data['in_days'] = int(data['joining_date'].day)-int(date.today().day)
            # print(birthday_list)

            self.response_format['status'] = True
            self.response_format['data'] = anniversary_list
            return Response(self.response_format, status=status.HTTP_200_OK)

        self.response_format['status'] = True
        self.response_format['data'] = 'there is no work anniversary of employees in this month'
        return Response(self.response_format, status=status.HTTP_200_OK)


class UpcomingThisMonthHoliday(APIView):

    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        self.response_format = ResponseFormat().response
        super().__init__(**kwargs)

    def get(self, request, *args, **kwargs):

        holiday_list = Holiday.objects.filter(date__month=date.today().month, date__gte=date.today()).values('name', 'date', 'description', 'type').order_by('date')

        if holiday_list:
            for data in holiday_list:
                data['in_days'] = (data['date'] - date.today()).days
                if data['type'] == 1:
                    data['type'] = 'half_day'
                else:
                    data['type'] = 'full_day'

            self.response_format['status'] = True
            self.response_format['data'] = holiday_list
            return Response(self.response_format, status=200)

        self.response_format['status'] = False
        self.response_format['data'] = 'No holidays left for this month.'
        return Response(self.response_format, status=200)
