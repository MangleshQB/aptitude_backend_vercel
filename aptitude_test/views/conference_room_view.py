import calendar
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, views, permissions
from rest_framework import viewsets
from aptitude_test.models import Conference
from aptitude_test.serializers import ConferenceRoomViewSerializer
from utils.common import ResponseFormat
import datetime as d1
from datetime import datetime, timedelta, date
from utils.views import CustomModelViewSet


class ConferenceRoomView(CustomModelViewSet):
    queryset = Conference.objects.all()
    serializer_class = ConferenceRoomViewSerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        self.response_format = ResponseFormat().response
        super().__init__(**kwargs)

    def list(self, request, *args, **kwargs):

        month = int(request.GET.get('month'))
        year = int(request.GET.get('year'))

        first_day = date(year, month, 1)
        last_day = date(year, month, calendar.monthrange(year, month)[1])

        queryset = self.queryset.filter(start_date__range=[first_day, last_day])

        serializer = self.get_serializer(queryset, many=True)

        self.response_format['data'] = serializer.data
        self.response_format['status'] = True
        return Response(self.response_format, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = self.serializer_class(data=data, context={'user': request.user, 'created_by':request.user})
        if serializer.is_valid(raise_exception=True):
            serializer.save()

            # self.response_format['data'] = serializer.data
            self.response_format['message'] = 'Conference data created successfully'
            self.response_format['status'] = True
            return Response(self.response_format, status=status.HTTP_201_CREATED)

        self.response_format['data'] = serializer.errors
        self.response_format['status'] = False
        return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        data = request.data
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.serializer_class(data=data, context={'user': request.user, 'updated_by':request.user}, instance=instance, partial=partial)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            # self.response_format['data'] = serializer.data
            self.response_format['message'] = 'Conference data Updated successfully'
            self.response_format['status'] = True
            return Response(self.response_format, status=status.HTTP_201_CREATED)

        self.response_format['data'] = serializer.errors
        self.response_format['status'] = False
        return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):

        conference = self.get_object()
        type = request.query_params['type']
        event_code = conference.event_code

        start_date = conference.start_date
        current_date = d1.datetime.now().date()
        if current_date > start_date:
            self.response_format['error'] = 'Cannot delete old events!'
            self.response_format['status'] = False
            return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)

        if type == 'delete_all':
            all_delete = Conference.objects.filter(event_code=event_code, start_date__gte=current_date)
            all_delete.delete()
        else:
            single_delete = Conference.objects.filter(event_code=event_code, start_date=start_date)
            single_delete.delete()

        self.response_format['message'] = 'Conference data deleted successfully'
        self.response_format['status'] = True
        return Response(self.response_format, status=status.HTTP_200_OK)
