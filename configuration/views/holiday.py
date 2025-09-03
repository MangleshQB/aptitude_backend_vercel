from rest_framework import viewsets, status
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from configuration.models import Holiday
from configuration.serializers import HolidaySerializer
from utils.views import CustomModelViewSet
from datetime import datetime , date


class HolidayViewSet(CustomModelViewSet):
    queryset = Holiday.objects.filter(is_deleted=False).order_by('-id')
    serializer_class = HolidaySerializer
    permission_classes = [IsAuthenticated]

    filter_backends = (SearchFilter,)
    search_fields = [
        'name',
        'date',
        'type',
        'description',
        'repeats_annually',
    ]

    ordering_fields = [
        'name',
        'date',
        'type',
        'description',
        'repeats_annually',
    ]

    def list(self, request, *args, **kwargs):

        self.queryset = self.queryset.filter(date__gte=date.today()).order_by('-id')

        if request.GET.get("search", None) or request.GET.get("ordering", None):
            queryset = self.filter_queryset(self.queryset)
        else:
            queryset = self.queryset

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
