from decimal import Decimal
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, views, permissions
from aptitude_test.models import TestPaper, PersonsAnswers
from aptitude_test.serializers import TestPaperUpdateSerializer
from utils.common import ResponseFormat

class TestPaperUpdate(APIView):
    queryset = TestPaper.objects.all().order_by('-id')
    serializer_class = TestPaperUpdateSerializer

    def __init__(self, **kwargs):
        self.response_format = ResponseFormat().response
        super().__init__(**kwargs)

    def post(self, request, *args, **kwargs):

        question_data = request.data
        testPaper_id = question_data['testPaper_id']
        person_ans_id = question_data['person_ans_id']
        test_paper = self.queryset.filter(id=testPaper_id)

        try:

            test_paper = TestPaper.objects.get(id=testPaper_id)
            question = PersonsAnswers.objects.get(id=person_ans_id)

            if not question.is_partially_correct and not question.is_correct and not question.is_wrong:

                if question_data["selected_option"]['correct']:
                    question.is_partially_correct = False
                    question.is_correct = True
                    test_paper.final_result += Decimal('1')
                    test_paper.total_correct_answers += 1

                if question_data["selected_option"]['partially_correct']:
                    question.is_partially_correct = True
                    question.is_correct = False
                    test_paper.final_result += Decimal('0.5')
                    test_paper.total_partially_correct_answers += 1

                if question_data["selected_option"]['wrong']:
                    question.is_wrong = True
                    test_paper.total_wrong_answers += 1

            else:

                if question.is_partially_correct and question_data["selected_option"]['correct']:
                    question.is_partially_correct = False
                    question.is_correct = True
                    test_paper.final_result += Decimal('0.5')
                    test_paper.total_partially_correct_answers -= 1
                    test_paper.total_correct_answers += 1

                elif question.is_correct and question_data["selected_option"]['partially_correct']:
                    question.is_partially_correct = True
                    question.is_correct = False
                    test_paper.final_result -= Decimal('0.5')
                    test_paper.total_partially_correct_answers += 1
                    test_paper.total_correct_answers -= 1

                elif question.is_correct and question_data["selected_option"]['wrong']:
                    question.is_partially_correct = False
                    question.is_correct = False
                    question.is_wrong = True
                    test_paper.final_result -= Decimal('1')
                    test_paper.total_correct_answers -= 1
                    test_paper.total_wrong_answers += 1

                elif question.is_partially_correct and question_data["selected_option"]['wrong']:
                    question.is_partially_correct = False
                    question.is_correct = False
                    question.is_wrong = True
                    test_paper.final_result -= Decimal('0.5')
                    test_paper.total_partially_correct_answers -= 1
                    test_paper.total_wrong_answers += 1

                elif question.is_wrong and question_data["selected_option"]['correct']:
                    question.is_partially_correct = False
                    question.is_correct = True
                    question.is_wrong = False
                    test_paper.total_correct_answers += 1
                    test_paper.final_result += Decimal('1')
                    test_paper.total_wrong_answers -= 1

                elif question.is_wrong and question_data["selected_option"]['partially_correct']:
                    question.is_partially_correct = True
                    question.is_correct = False
                    question.is_wrong = False
                    test_paper.total_partially_correct_answers += 1
                    test_paper.total_wrong_answers -= 1
                    test_paper.final_result += Decimal('0.5')

            question.save()
            test_paper.save()
            serializer = self.serializer_class(test_paper)
            self.response_format['data'] = serializer.data
            self.response_format['status'] = True
            return Response(self.response_format, status=status.HTTP_200_OK)

        except Exception as e:

            print(e)

            self.response_format['error'] = 'Test paper not found'
            self.response_format['data'] = e
            self.response_format['status'] = False
            return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)

    # def handle_exception(self, exc):
    #     if isinstance(exc, (AuthenticationFailed, ParseError, ValidationError)):
    #         return Response({'message': 'Unauthorized user'}, status=status.HTTP_401_UNAUTHORIZED)
    #     return super().handle_exception(exc)
