from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView

from rest_framework.response import Response
from rest_framework import status, permissions

from configuration.serializers import UserAppVersionSerializer
from utils.common import ResponseFormat


class UserAppVersionView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def __init__(self, **kwargs):
        self.response_format = ResponseFormat().response
        super().__init__(**kwargs)

    def post(self, request):

        data = dict(request.data)
        data['user'] = request.user.id
        serializer = UserAppVersionSerializer(data=data, context={'created_by': request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        self.response_format["status"] = True
        self.response_format["data"] = serializer.data
        return Response(self.response_format, status=status.HTTP_200_OK)