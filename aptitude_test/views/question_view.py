from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, views, permissions
from rest_framework import viewsets
from rest_framework import filters
from aptitude_test.models import Questions
from aptitude_test.serializers import QuestionSerializer
from utils.common import ResponseFormat
from utils.views import CustomModelViewSet


class Pagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class QuestionViewSet(CustomModelViewSet):
    pagination_class = Pagination
    permission_classes = [IsAuthenticated]
    queryset = Questions.objects.all().order_by('-id')
    serializer_class = QuestionSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['question']

    def __init__(self, **kwargs):
        self.response_format = ResponseFormat().response
        super().__init__(**kwargs)

    def get_queryset(self):
        user = self.request.user
        designation = self.request.GET.get("designation", user.designation.id)
        return Questions.objects.filter(designation_id=designation).order_by('-id')

    def create(self, request, *args, **kwargs):
        user = request.user
        designation = user.designation
        data = request.data
        data['designation'] = designation.id
        serializer = self.get_serializer(data=data,context={'created_by': request.user})
        serializer.is_valid(raise_exception=True)
        # self.perform_create(serializer)
        serializer.save(designation=designation)

        self.response_format['data'] = serializer.data
        self.response_format['status'] = True
        return Response(self.response_format, status=status.HTTP_201_CREATED)

    # def perform_create(self, serializer):
    #     user = self.request.user
    #     designation = user.designation
    #     serializer.save(designation=designation)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        self.response_format['data'] = serializer.data
        self.response_format['status'] = True
        return Response(self.response_format, status=status.HTTP_200_OK)

    # def handle_exception(self, exc):
    #     if isinstance(exc, (AuthenticationFailed, ParseError, ValidationError)):
    #         return Response({'message': 'Unauthorized user'}, status=status.HTTP_401_UNAUTHORIZED)
    #     return super().handle_exception(exc)