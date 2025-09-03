from aptitude_test.models import Configuration, Questions
from aptitude_test.serializers import QuestionSerializer, RandomSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework import status, views, permissions
from rest_framework.exceptions import AuthenticationFailed, ParseError, ValidationError
from utils.common import ResponseFormat


class RandomQuestion(generics.ListAPIView):
    serializer_class = RandomSerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        self.response_format = ResponseFormat().response
        super().__init__(**kwargs)

    def get(self, request, *args, **kwargs):

        user = request.user
        designation = request.GET.get("designation", None)
        difficulty = request.GET.get("difficulty", None)

        if designation:

            configuration = Configuration.objects.filter(designation_id=designation).first()
            num_questions = configuration.no_questions_to_asked if configuration and configuration.no_questions_to_asked else 10
            queryset = Questions.objects.filter(designation_id=designation, difficulty=difficulty)
            num_que = len(queryset)

            if num_que < num_questions:
                return Response({'error': 'Not enough questions available '}, status=status.HTTP_400_BAD_REQUEST)

            aptitude_count = int(num_questions * 0.30)
            technical_text_count = int(num_questions * 0.35)
            technical_choice_count = num_questions - (aptitude_count + technical_text_count)

            aptitude_questions = list(queryset.filter(question_type='aptitude').order_by('?')[:aptitude_count])
            text_questions = list(
                queryset.filter(type='text_area', question_type='technical').order_by('?')[:technical_text_count])
            choice_questions = list(
                queryset.filter(type='choices', question_type='technical').order_by('?')[:technical_choice_count])

            queryset = aptitude_questions + text_questions + choice_questions

            serializer = QuestionSerializer(queryset, many=True)

            self.response_format['data'] = serializer.data
            self.response_format['status'] = True
            return Response(self.response_format, status=status.HTTP_200_OK)

        self.response_format['error'] = 'No designation found for the user check it'
        self.response_format['status'] = False
        return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)

    def handle_exception(self, exc):
        if isinstance(exc, (AuthenticationFailed, ParseError, ValidationError)):
            return Response({'message': 'Unauthorized user'}, status=status.HTTP_401_UNAUTHORIZED)
        return super().handle_exception(exc)

