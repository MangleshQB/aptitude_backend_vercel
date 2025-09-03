from rest_framework.views import APIView
from rest_framework import status
from app.management.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from app.models import CustomUser
from utils.common import ResponseFormat


class CheckExistUsername(APIView):
    permission_classes = [IsAuthenticated]
    def __init__(self, **kwargs):
        self.response_format = ResponseFormat().response
        super().__init__(**kwargs)

    def post(self, request):

        data = request.data

        username = data.get('username', None)
        check_username = CustomUser.objects.filter(username__iexact=username).exists()

        email_id = data.get('email', None)
        check_email = CustomUser.objects.filter(email__iexact=email_id).exists()

        if check_username and check_email:

            self.response_format['status'] = False
            self.response_format['message'] = 'Username and Email Already Exists'
            return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)
        else:
            if check_username:
                self.response_format['status'] = False
                self.response_format['message'] = 'Username Already Exists'
                return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)
            elif check_email:
                self.response_format['status'] = False
                self.response_format['message'] = 'Email Already Exists'
                return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)
            else:
                self.response_format['status'] = True
                self.response_format['message'] = 'Username and Email do not Exist'
                return Response(self.response_format, status=status.HTTP_200_OK)
