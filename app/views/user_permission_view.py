from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from app.management.authentication import JWTAuthentication
from app.models import AllowedContentType
from app.serializers import CustomUserSerializerForPermission
from utils.common import ResponseFormat


class UserPermissionView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def __init__(self, **kwargs):
        self.response_format = ResponseFormat().response
        super().__init__(**kwargs)

    def get(self, request):

        user = request.user

        allowed_content_type_ids = list(AllowedContentType.objects.values_list('content_type_id', flat=True))
        permissions = request.user.groups.first().permissions.filter(content_type_id__in=allowed_content_type_ids)

        ctx = {}

        for p in permissions:
            if p.content_type.name not in ctx.keys():
                ctx[p.content_type.name] = [p.codename.split('_')[0]]
            else:
                ctx[p.content_type.name].append(p.codename.split('_')[0])

        self.response_format['status'] = True
        self.response_format['data'] = ctx
        self.response_format['user'] = CustomUserSerializerForPermission(user).data

        return Response(self.response_format, status=status.HTTP_200_OK)
