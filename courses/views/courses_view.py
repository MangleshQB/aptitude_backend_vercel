from rest_framework import status, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from courses.models import Courses, Videos
from courses.serializer import CoursesSerializer, CoursesWithVideoSerializer
from utils.common import ResponseFormat
from utils.views import CustomModelViewSet


class Pagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class CoursesView(CustomModelViewSet):

    def __init__(self, **kwargs):
        self.response_format = ResponseFormat().response
        super(CustomModelViewSet, self).__init__(**kwargs)

    queryset = Courses.objects.all().order_by('-id')
    serializer_class = CoursesWithVideoSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = Pagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'topic__name', 'presenter__name', 'languages__name']


    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CoursesSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = CoursesSerializer(queryset, many=True)
        # return Response(serializer.data)
        self.response_format["data"] = serializer.data
        self.response_format["status"] = True
        if not serializer.data:
            self.response_format["message"] = "No data found!"
        return Response(self.response_format, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):

        instance = self.get_object()
        category = list(instance.videos.all().values_list('category__id', 'category__name').distinct())
        serializer = self.get_serializer(instance)

        ctx = {}

        for cat in category:

            cat_list = list(
                Videos.objects.filter(category_id=cat[0]).values('id', 'title', 'duration', 'description', 'file',
                                                                 'order', 'category', 'thumbnail'))

            total_seconds = int(cat_list[0]['duration'].total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            cat_list[0]['duration'] = f"{hours:02}:{minutes:02}:{seconds:02}"

            ctx[cat[1]] = cat_list

        data = serializer.data
        data['videos'] = ctx

        # return Response(data)
        self.response_format["data"] = serializer.data
        self.response_format["status"] = True
        if not serializer.data:
            self.response_format["message"] = "No data found!"
        return Response(self.response_format, status=status.HTTP_200_OK)