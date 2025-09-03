from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, views, permissions
from rest_framework import viewsets
from aptitude_test.serializers import EmployeeSerializer
from utils.common import ResponseFormat
from app.models import CustomUser
from utils.views import CustomModelViewSet


class EmployeeViewSet(CustomModelViewSet):
    # queryset = Employee.objects.all()
    queryset = CustomUser.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        self.response_format = ResponseFormat().response
        super().__init__(**kwargs)

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = self.serializer_class(data=data, context={'user': request.user})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            self.response_format['data'] = serializer.data
            self.response_format['message'] = 'Conference data created successfully'
            self.response_format['status'] = True
            return Response(self.response_format, status=status.HTTP_201_CREATED)

        self.response_format['data'] = serializer.errors
        self.response_format['status'] = False
        return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)
