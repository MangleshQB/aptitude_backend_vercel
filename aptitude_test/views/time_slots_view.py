import datetime
from datetime import timedelta, datetime

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from aptitude_test.models import Configuration, Conference
from utils.common import ResponseFormat


class TimeSlotsView(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        self.response_format = ResponseFormat().response
        super().__init__(**kwargs)

    def get(self, request, *args, **kwargs):

        designation = request.user.designation
        date = request.GET.get('date')

        date = datetime.strptime(date, '%Y-%m-%d').date()
        office_time = Configuration.objects.filter(designation=designation).first()
        conference_date = list(Conference.objects.filter(start_date=date).values('start_time', 'end_time'))
        if not office_time:
            self.response_format['error'] = 'office time not found'
            self.response_format['status'] = False
            return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)
        office_start = office_time.office_start
        office_end = office_time.office_end

        start_time = datetime.combine(datetime.today(), office_start)
        end_time = datetime.combine(datetime.today(), office_end)

        time_slots = []
        while start_time != end_time:

            slots = {
                'start_time': start_time.time()
            }

            start_time = start_time + timedelta(minutes=15)
            slots['end_time'] = start_time.time()

            if slots in conference_date:
                pass
            else:
                slots['start_time'] = slots['start_time'].strftime('%H:%M')
                slots['end_time'] = slots['end_time'].strftime('%H:%M')
                time_slots.append(slots)

        self.response_format['data'] = time_slots
        self.response_format['status'] = True
        return Response(self.response_format, status=status.HTTP_200_OK)
