from rest_framework import status, views, permissions, serializers, filters
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from django.contrib.auth.models import Group, Permission

from app.models import AllowedContentType
from app.serializers import PermissionSerializer
from utils.common import ResponseFormat
from utils.views import CustomModelViewSet


class PermissionsView(CustomModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer

    def __init__(self, **kwargs):
        self.response_format = ResponseFormat().response
        super().__init__(**kwargs)

    def list(self, request, *args, **kwargs):

        content_type_list = list(
            AllowedContentType.objects.filter(is_active=True).values_list('content_type_id', flat=True))

        ctx = {}

        for content_type in content_type_list:
            permissions = list(Permission.objects.filter(content_type=content_type).values())
            for permission in permissions:
                permission['value'] = permission['codename'].split('_')[0]
            name = (' '.join(((permissions[0]['name']).split())[2:])).title()
            ctx[name] = permissions

        self.response_format['status'] = True
        self.response_format['data'] = ctx
        return Response(self.response_format, status=status.HTTP_200_OK)
