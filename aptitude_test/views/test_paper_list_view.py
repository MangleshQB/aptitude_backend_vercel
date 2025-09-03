from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework import status, views, permissions
from rest_framework import filters
from rest_framework.exceptions import AuthenticationFailed, ParseError, ValidationError
from aptitude_test.models import TestPaper
from aptitude_test.serializers import TestPaperSerializer
from utils.common import ResponseFormat


class Pagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class TestPaperListView(generics.ListCreateAPIView):
    queryset = TestPaper.objects.all().order_by('-id')
    serializer_class = TestPaperSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = Pagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['person__name']

    def __init__(self, **kwargs):
        self.response_format = ResponseFormat().response
        super().__init__(**kwargs)

    def get(self, request, *args, **kwargs):

        designation = request.user.designation
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(person__designation=designation)
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        self.response_format['data'] = serializer.data
        self.response_format['status'] = True
        return Response(self.response_format, status=status.HTTP_200_OK)

    def handle_exception(self, exc):

        if isinstance(exc, (AuthenticationFailed, ParseError, ValidationError)):
            return Response({'message': 'Unauthorized user'}, status=status.HTTP_401_UNAUTHORIZED)
        return super().handle_exception(exc)
