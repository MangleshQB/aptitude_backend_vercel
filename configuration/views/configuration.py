from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from configuration.models import SoftwareConfiguration
from configuration.serializers import ConfigurationSerializer
from utils.common import ResponseFormat
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication

from utils.views import CustomModelViewSet


# class ConfigurationView(ModelViewSet):
#     queryset = SoftwareConfiguration.objects.all()
#     permission_classes = [IsAuthenticated]
#     serializer_class = ConfigurationSerializer


class ConfigurationViewAptitude(CustomModelViewSet):
    queryset = SoftwareConfiguration.objects.all()
    serializer_class = ConfigurationSerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        self.response_format = ResponseFormat().response
        super().__init__(**kwargs)

    def list(self, request, *args, **kwargs):
        configurations = SoftwareConfiguration.objects.all().first()
        serializer = ConfigurationSerializer(configurations, many=False)
        self.response_format['data'] = serializer.data
        self.response_format['status'] = True
        return Response(self.response_format, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        configurations = SoftwareConfiguration.objects.all().first()
        serializer = ConfigurationSerializer(configurations, data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()

            self.response_format['data'] = serializer.data
            self.response_format['status'] = True
            return Response(self.response_format, status=status.HTTP_200_OK)

        self.response_format['error'] = 'Update Error'
        self.response_format['data'] = serializer.errors
        self.response_format['status'] = False
        return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)


class ConfigurationViewSurveillance(viewsets.ModelViewSet):
    queryset = SoftwareConfiguration.objects.all()
    serializer_class = ConfigurationSerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        self.response_format = ResponseFormat().response
        super().__init__(**kwargs)

    def list(self, request, *args, **kwargs):
        is_surveillance_active = request.user.is_surveillance_active
        configurations = SoftwareConfiguration.objects.all().first()
        serializer = ConfigurationSerializer(configurations, many=False)
        response_data = serializer.data
        response_data['is_surveillance_active'] = is_surveillance_active
        self.response_format['data'] = response_data
        self.response_format['status'] = True
        return Response(self.response_format, status=status.HTTP_200_OK)

