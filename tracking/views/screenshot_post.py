from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from tracking.serializer import ScreenshotsSerializer
from utils.common import ResponseFormat
from rest_framework.response import Response
from rest_framework import status

class ScreenshotsView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = ScreenshotsSerializer

    def __init__(self, **kwargs):
        self.response_format = ResponseFormat().response
        super().__init__(**kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'user': request.user, 'created_by':request.user})

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            self.response_format['data'] = serializer.data
            self.response_format['status'] = True
            return Response(self.response_format, status=status.HTTP_200_OK)
        self.response_format['status'] = False
        self.response_format['error'] = serializer.errors
        return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)
