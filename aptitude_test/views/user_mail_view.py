from rest_framework.response import Response
from rest_framework import status, views, permissions
from rest_framework.viewsets import ModelViewSet

from aptitude_test.serializers import UserEmailSerializer
from utils.common import ResponseFormat
from app.models import CustomUser
from utils.middlewares import CheckSoftwareUser
from utils.views import CustomModelViewSet


class UserMail(CustomModelViewSet):
    serializer_class = UserEmailSerializer
    permission_classes = [CheckSoftwareUser]

    def __init__(self, **kwargs):
        self.response_format = ResponseFormat().response
        super().__init__(**kwargs)

    def list(self, request, *args, **kwargs):
        mail = request.GET.get('mail')
        user = CustomUser.objects.filter(email=mail).first()
        if user:
            user.is_using_surveillance_software = True
            user.save()
            self.response_format['status'] = True
            self.response_format['data'] = user.email
            return Response(self.response_format, status=status.HTTP_200_OK)
        else:
            self.response_format['status'] = False
            self.response_format['data'] = 'User Does not exist'
            return Response(self.response_format, status=status.HTTP_404_NOT_FOUND)
