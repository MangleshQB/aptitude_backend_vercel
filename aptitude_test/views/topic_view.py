from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, views, permissions
from rest_framework import viewsets

from aptitude_test.models import Topic
from aptitude_test.serializers import TopicViewSetSerializer
from utils.common import ResponseFormat
from utils.views import CustomModelViewSet


class TopicViewSet(CustomModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Topic.objects.all()
    serializer_class = TopicViewSetSerializer

    def __init__(self, **kwargs):
        self.response_format = ResponseFormat().response
        super().__init__(**kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'user': request.user, 'created_by':request.user})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            self.response_format['data'] = serializer.data
            self.response_format['message'] = 'Topic created successfully'
            self.response_format['status'] = True
            return Response(self.response_format, status=status.HTTP_201_CREATED)

        self.response_format['data'] = serializer.errors
        self.response_format['status'] = False
        return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True, context={'user': request.user, 'updated_by':request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        self.response_format['message'] = 'Conference data deleted successfully'
        self.response_format['status'] = True
        self.response_format['data'] = serializer.data
        return Response(self.response_format, status=status.HTTP_200_OK)
