from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, views, permissions
from drf_yasg.utils import swagger_auto_schema
from aptitude_test.serializers import CreateQuestionSerializer
from utils.common import ResponseFormat


class CreateQuestion(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = CreateQuestionSerializer

    def __init__(self, **kwargs):
        self.response_format = ResponseFormat().response
        super().__init__(**kwargs)

    @swagger_auto_schema(request_body=CreateQuestionSerializer, operation_description="Create Question API", )
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'created_by': request.user})

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            self.response_format['message'] = 'Question created successfully'
            self.response_format['status'] = True
            self.response_format['data'] = serializer.data
            return Response(self.response_format, status=status.HTTP_201_CREATED)

        self.response_format['error'] = 'Error occurred during Question Created'
        self.response_format['data'] = serializer.errors
        self.response_format['status'] = False
        return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)
