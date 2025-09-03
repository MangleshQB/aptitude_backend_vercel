from aptitude_test.models import Configuration
from aptitude_test.serializers import AptitudeConfigurationSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, views, permissions
from rest_framework import viewsets
from rest_framework.exceptions import AuthenticationFailed, ParseError, ValidationError
from utils.common import ResponseFormat
from utils.views import CustomModelViewSet


class ConfigurationView(CustomModelViewSet):
    queryset = Configuration.objects.all()
    serializer_class = AptitudeConfigurationSerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        self.response_format = ResponseFormat().response
        super().__init__(**kwargs)

    def list(self, request, *args, **kwargs):

        configurations = Configuration.objects.filter(designation=request.user.designation).first()
        serializer = AptitudeConfigurationSerializer(configurations, many=False)
        self.response_format['data'] = serializer.data
        self.response_format['status'] = True
        return Response(self.response_format, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):

        configurations = Configuration.objects.filter(designation=request.user.designation).first()
        serializer = AptitudeConfigurationSerializer(configurations, data=request.data, context={'updated_by': request.user})

        if serializer.is_valid(raise_exception=True):
            serializer.save()

            self.response_format['data'] = serializer.data
            self.response_format['status'] = True
            return Response(self.response_format, status=status.HTTP_200_OK)

        self.response_format['error'] = 'Update Error'
        self.response_format['data'] = serializer.errors
        self.response_format['status'] = False
        return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)

    def handle_exception(self, exc):

        if isinstance(exc, (AuthenticationFailed, ParseError, ValidationError)):
            return Response({'message': 'Unauthorized user'}, status=status.HTTP_401_UNAUTHORIZED)
        return super().handle_exception(exc)

