import calendar
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, views, permissions
from aptitude_test.models import Conference
from aptitude_test.serializers import UpcomingConferenceSerializer
from utils.common import ResponseFormat
import datetime
from datetime import datetime, timedelta, date


class UpcomingConferenceView(views.APIView):
    queryset = Conference.objects.all().order_by('start_date', 'start_time')
    serializer_class = UpcomingConferenceSerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        self.response_format = ResponseFormat().response
        super().__init__(**kwargs)

    def get(self, request, *args, **kwargs):
        month = int(request.GET.get('month'))
        year = int(request.GET.get('year'))

        today = datetime.now().date()
        current_time = datetime.now().time()
        last_day = date(year, month, calendar.monthrange(year, month)[1])

        today_events = self.queryset.filter(
            start_date=today, start_time__gte=current_time
        ).order_by('start_time')

        future_events = self.queryset.filter(
            start_date__range=[today + timedelta(days=1), last_day]
        ).order_by('start_date', 'start_time')

        queryset = list(today_events) + list(future_events)

        serializer = self.serializer_class(queryset, many=True)
        all_data = serializer.data

        for index, data in enumerate(all_data):
            data['index'] = index + 1

        self.response_format['data'] = all_data
        self.response_format['status'] = True
        return Response(self.response_format, status=status.HTTP_200_OK)

    # def get(self, request, *args, **kwargs):
    #     month = int(request.GET.get('month'))
    #     year = int(request.GET.get('year'))
    #
    #     today = datetime.now().date()
    #     current_time = datetime.now().time()
    #     last_day = date(year, month, calendar.monthrange(year, month)[1])
    #
    #     queryset = self.queryset.filter(start_date__range=[today, last_day]).exclude(start_date=today, start_time__gt=current_time)
    #
    #     serializer = self.serializer_class(queryset, many=True)
    #
    #     all_data = serializer.data
    #
    #     for index, data in enumerate(all_data):
    #         data['index'] = index + 1
    #         # print(data['index'])
    #
    #     self.response_format['data'] = all_data
    #     self.response_format['status'] = True
    #     return Response(self.response_format, status=status.HTTP_201_CREATED)