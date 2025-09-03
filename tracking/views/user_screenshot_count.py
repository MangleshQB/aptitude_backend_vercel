from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework import permissions
from tracking.serializer import UserScreenshotCountSerializer
from tracking.models import UserScreenshots
from utils.common import ResponseFormat


class UserScreenshotCountView(APIView):
    serializer_class = UserScreenshotCountSerializer
    permission_classes = [permissions.IsAuthenticated]

    # authentication_classes = [TokenAuthentication]
    def __init__(self, **kwargs):
        self.response_format = ResponseFormat().response
        super().__init__(**kwargs)

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data.get('email')
            screenshot_count = UserScreenshots.objects.filter(user__email=email).values('file').count()
            print(screenshot_count)

            self.response_format['status'] = True
            self.response_format['message'] = 'Success'
            self.response_format['data'] = {'screenshot_count': screenshot_count}
            return Response(self.response_format, status=status.HTTP_200_OK)

        self.response_format['status'] = False
        self.response_format['error'] = serializer.errors
        return Response(self.response_format, status=status.HTTP_200_OK)
