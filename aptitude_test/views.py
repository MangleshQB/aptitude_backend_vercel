# import calendar
# from decimal import Decimal
# from django.http import JsonResponse
# from rest_framework.pagination import PageNumberPagination
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.views import APIView
# from rest_framework import generics
# from rest_framework import status, views, permissions
# from drf_yasg.utils import swagger_auto_schema
# from rest_framework import viewsets
# from rest_framework import filters
# from rest_framework.exceptions import AuthenticationFailed, ParseError, ValidationError
# from rest_framework.viewsets import ModelViewSet
#
# from utils.common import ResponseFormat
# from app.models import CustomUser
# from utils.middlewares import CheckSoftwareUser
# # from .models import Holiday
# from .serializers import QuestionSerializer, QuestionSerializer, CreateQuestionSerializer, TestPaperSerializer, \
#     ConfigurationSerializer, TestPaperUpdateSerializer, ConferenceRoomViewSerializer, EmployeeSerializer, \
#     TopicViewSetSerializer, UpcomingConferenceSerializer, getTopPresenterSerializer, getTopTopicsSerializer, \
#     UserEmailSerializer
# from .models.conference import Conference
# from .models.configuration import Configuration
# from .models.person_answer import PersonsAnswers
# from .models.questions import Questions
# from .models.test_paper import TestPaper
# from .models.topic import Topic
# from .serializers import RandomSerializer
# import datetime as d1
# import datetime
# from datetime import datetime, timedelta, date
# from django.db.models import Q, Count, F
#
# from rest_framework.filters import SearchFilter
#
#
# class CreateQuestion(APIView):
#     permission_classes = [permissions.AllowAny]
#     serializer_class = CreateQuestionSerializer
#
#     def __init__(self, **kwargs):
#         self.response_format = ResponseFormat().response
#         super().__init__(**kwargs)
#
#     @swagger_auto_schema(request_body=CreateQuestionSerializer, operation_description="Create Question API", )
#     def post(self, request):
#         serializer = self.serializer_class(data=request.data)
#
#         if serializer.is_valid(raise_exception=True):
#             serializer.save()
#             self.response_format['message'] = 'Question created successfully'
#             self.response_format['status'] = True
#             self.response_format['data'] = serializer.data
#             return Response(self.response_format, status=status.HTTP_201_CREATED)
#
#         self.response_format['error'] = 'Error occurred during Question Created'
#         self.response_format['data'] = serializer.errors
#         self.response_format['status'] = False
#         return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)
#
#
# class Pagination(PageNumberPagination):
#     page_size = 10
#     page_size_query_param = 'page_size'
#     max_page_size = 100
#
#
# class QuestionViewSet(viewsets.ModelViewSet):
#     pagination_class = Pagination
#     permission_classes = [IsAuthenticated]
#     queryset = Questions.objects.all().order_by('-id')
#     serializer_class = QuestionSerializer
#     filter_backends = [filters.SearchFilter]
#     search_fields = ['question']
#
#     def __init__(self, **kwargs):
#         self.response_format = ResponseFormat().response
#         super().__init__(**kwargs)
#
#     def get_queryset(self):
#         user = self.request.user
#         designation = self.request.GET.get("designation", user.designation.id)
#         return Questions.objects.filter(designation_id=designation).order_by('-id')
#
#     def create(self, request, *args, **kwargs):
#         user = request.user
#         designation = user.designation
#         data = request.data
#         data['designation'] = designation.id
#         serializer = self.get_serializer(data=data)
#         serializer.is_valid(raise_exception=True)
#         # self.perform_create(serializer)
#         serializer.save(designation=designation)
#
#         self.response_format['data'] = serializer.data
#         self.response_format['status'] = True
#         return Response(self.response_format, status=status.HTTP_201_CREATED)
#
#     # def perform_create(self, serializer):
#     #     user = self.request.user
#     #     designation = user.designation
#     #     serializer.save(designation=designation)
#
#     def update(self, request, *args, **kwargs):
#         partial = kwargs.pop('partial', False)
#         instance = self.get_object()
#         serializer = self.get_serializer(instance, data=request.data, partial=partial)
#         serializer.is_valid(raise_exception=True)
#         self.perform_update(serializer)
#         self.response_format['data'] = serializer.data
#         self.response_format['status'] = True
#         return Response(self.response_format, status=status.HTTP_200_OK)
#
#     # def handle_exception(self, exc):
#     #     if isinstance(exc, (AuthenticationFailed, ParseError, ValidationError)):
#     #         return Response({'message': 'Unauthorized user'}, status=status.HTTP_401_UNAUTHORIZED)
#     #     return super().handle_exception(exc)
#
#
# # class TestPaperCreateView(generics.CreateAPIView):
# #     queryset = TestPaper.objects.all()
# #     serializer_class = TestPaperSerializer
#
#
# class TestPaperListView(generics.ListCreateAPIView):
#     queryset = TestPaper.objects.all().order_by('-id')
#     serializer_class = TestPaperSerializer
#     permission_classes = [IsAuthenticated]
#     pagination_class = Pagination
#     filter_backends = [filters.SearchFilter]
#     search_fields = ['person__name']
#
#     def __init__(self, **kwargs):
#         self.response_format = ResponseFormat().response
#         super().__init__(**kwargs)
#
#     def get(self, request, *args, **kwargs):
#
#         designation = request.user.designation
#         queryset = self.filter_queryset(self.get_queryset())
#         queryset = queryset.filter(person__designation=designation)
#         page = self.paginate_queryset(queryset)
#
#         if page is not None:
#             serializer = self.get_serializer(page, many=True)
#             return self.get_paginated_response(serializer.data)
#
#         serializer = self.get_serializer(queryset, many=True)
#         self.response_format['data'] = serializer.data
#         self.response_format['status'] = True
#         return Response(self.response_format, status=status.HTTP_200_OK)
#
#     def handle_exception(self, exc):
#
#         if isinstance(exc, (AuthenticationFailed, ParseError, ValidationError)):
#             return Response({'message': 'Unauthorized user'}, status=status.HTTP_401_UNAUTHORIZED)
#         return super().handle_exception(exc)
#
#
# class TestPaperUpdate(APIView):
#     queryset = TestPaper.objects.all().order_by('-id')
#     serializer_class = TestPaperUpdateSerializer
#
#     def __init__(self, **kwargs):
#         self.response_format = ResponseFormat().response
#         super().__init__(**kwargs)
#
#     def post(self, request, *args, **kwargs):
#
#         question_data = request.data
#         testPaper_id = question_data['testPaper_id']
#         person_ans_id = question_data['person_ans_id']
#         test_paper = self.queryset.filter(id=testPaper_id)
#
#         try:
#
#             test_paper = TestPaper.objects.get(id=testPaper_id)
#             question = PersonsAnswers.objects.get(id=person_ans_id)
#
#             if not question.is_partially_correct and not question.is_correct and not question.is_wrong:
#
#                 if question_data["selected_option"]['correct']:
#                     question.is_partially_correct = False
#                     question.is_correct = True
#                     test_paper.final_result += Decimal('1')
#                     test_paper.total_correct_answers += 1
#
#                 if question_data["selected_option"]['partially_correct']:
#                     question.is_partially_correct = True
#                     question.is_correct = False
#                     test_paper.final_result += Decimal('0.5')
#                     test_paper.total_partially_correct_answers += 1
#
#                 if question_data["selected_option"]['wrong']:
#                     question.is_wrong = True
#                     test_paper.total_wrong_answers += 1
#
#             else:
#
#                 if question.is_partially_correct and question_data["selected_option"]['correct']:
#                     question.is_partially_correct = False
#                     question.is_correct = True
#                     test_paper.final_result += Decimal('0.5')
#                     test_paper.total_partially_correct_answers -= 1
#                     test_paper.total_correct_answers += 1
#
#                 elif question.is_correct and question_data["selected_option"]['partially_correct']:
#                     question.is_partially_correct = True
#                     question.is_correct = False
#                     test_paper.final_result -= Decimal('0.5')
#                     test_paper.total_partially_correct_answers += 1
#                     test_paper.total_correct_answers -= 1
#
#                 elif question.is_correct and question_data["selected_option"]['wrong']:
#                     question.is_partially_correct = False
#                     question.is_correct = False
#                     question.is_wrong = True
#                     test_paper.final_result -= Decimal('1')
#                     test_paper.total_correct_answers -= 1
#                     test_paper.total_wrong_answers += 1
#
#                 elif question.is_partially_correct and question_data["selected_option"]['wrong']:
#                     question.is_partially_correct = False
#                     question.is_correct = False
#                     question.is_wrong = True
#                     test_paper.final_result -= Decimal('0.5')
#                     test_paper.total_partially_correct_answers -= 1
#                     test_paper.total_wrong_answers += 1
#
#                 elif question.is_wrong and question_data["selected_option"]['correct']:
#                     question.is_partially_correct = False
#                     question.is_correct = True
#                     question.is_wrong = False
#                     test_paper.total_correct_answers += 1
#                     test_paper.final_result += Decimal('1')
#                     test_paper.total_wrong_answers -= 1
#
#                 elif question.is_wrong and question_data["selected_option"]['partially_correct']:
#                     question.is_partially_correct = True
#                     question.is_correct = False
#                     question.is_wrong = False
#                     test_paper.total_partially_correct_answers += 1
#                     test_paper.total_wrong_answers -= 1
#                     test_paper.final_result += Decimal('0.5')
#
#             question.save()
#             test_paper.save()
#             serializer = self.serializer_class(test_paper)
#             self.response_format['data'] = serializer.data
#             self.response_format['status'] = True
#             return Response(self.response_format, status=status.HTTP_200_OK)
#
#         except Exception as e:
#
#             print(e)
#
#             self.response_format['error'] = 'Test paper not found'
#             self.response_format['data'] = e
#             self.response_format['status'] = False
#             return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)
#
#     # def handle_exception(self, exc):
#     #     if isinstance(exc, (AuthenticationFailed, ParseError, ValidationError)):
#     #         return Response({'message': 'Unauthorized user'}, status=status.HTTP_401_UNAUTHORIZED)
#     #     return super().handle_exception(exc)
#
#
# class RandomQuestion(generics.ListAPIView):
#     serializer_class = RandomSerializer
#     permission_classes = [IsAuthenticated]
#
#     def __init__(self, **kwargs):
#         self.response_format = ResponseFormat().response
#         super().__init__(**kwargs)
#
#     def get(self, request, *args, **kwargs):
#
#         user = request.user
#         designation = request.GET.get("designation", None)
#         difficulty = request.GET.get("difficulty", None)
#
#         if designation:
#
#             configuration = Configuration.objects.filter(designation_id=designation).first()
#             num_questions = configuration.no_questions_to_asked if configuration and configuration.no_questions_to_asked else 10
#             queryset = Questions.objects.filter(designation_id=designation, difficulty=difficulty)
#             num_que = len(queryset)
#
#             if num_que < num_questions:
#                 return Response({'error': 'Not enough questions available '}, status=status.HTTP_400_BAD_REQUEST)
#
#             aptitude_count = int(num_questions * 0.30)
#             technical_text_count = int(num_questions * 0.35)
#             technical_choice_count = num_questions - (aptitude_count + technical_text_count)
#
#             aptitude_questions = list(queryset.filter(question_type='aptitude').order_by('?')[:aptitude_count])
#             text_questions = list(
#                 queryset.filter(type='text_area', question_type='technical').order_by('?')[:technical_text_count])
#             choice_questions = list(
#                 queryset.filter(type='choices', question_type='technical').order_by('?')[:technical_choice_count])
#
#             queryset = aptitude_questions + text_questions + choice_questions
#
#             serializer = QuestionSerializer(queryset, many=True)
#
#             self.response_format['data'] = serializer.data
#             self.response_format['status'] = True
#             return Response(self.response_format, status=status.HTTP_200_OK)
#
#         self.response_format['error'] = 'No designation found for the user check it'
#         self.response_format['status'] = False
#         return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)
#
#     def handle_exception(self, exc):
#         if isinstance(exc, (AuthenticationFailed, ParseError, ValidationError)):
#             return Response({'message': 'Unauthorized user'}, status=status.HTTP_401_UNAUTHORIZED)
#         return super().handle_exception(exc)
#
#
# class ConfigurationView(viewsets.ModelViewSet):
#     queryset = Configuration.objects.all()
#     serializer_class = ConfigurationSerializer
#     permission_classes = [IsAuthenticated]
#
#     def __init__(self, **kwargs):
#         self.response_format = ResponseFormat().response
#         super().__init__(**kwargs)
#
#     def list(self, request, *args, **kwargs):
#
#         configurations = Configuration.objects.filter(designation=request.user.designation).first()
#         serializer = ConfigurationSerializer(configurations, many=False)
#         self.response_format['data'] = serializer.data
#         self.response_format['status'] = True
#         return Response(self.response_format, status=status.HTTP_200_OK)
#
#     def update(self, request, *args, **kwargs):
#
#         configurations = Configuration.objects.filter(designation=request.user.designation).first()
#         serializer = ConfigurationSerializer(configurations, data=request.data)
#
#         if serializer.is_valid(raise_exception=True):
#             serializer.save()
#
#             self.response_format['data'] = serializer.data
#             self.response_format['status'] = True
#             return Response(self.response_format, status=status.HTTP_200_OK)
#
#         self.response_format['error'] = 'Update Error'
#         self.response_format['data'] = serializer.errors
#         self.response_format['status'] = False
#         return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)
#
#     def handle_exception(self, exc):
#
#         if isinstance(exc, (AuthenticationFailed, ParseError, ValidationError)):
#             return Response({'message': 'Unauthorized user'}, status=status.HTTP_401_UNAUTHORIZED)
#         return super().handle_exception(exc)
#
#
# class TimeSlotsView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def __init__(self, **kwargs):
#         self.response_format = ResponseFormat().response
#         super().__init__(**kwargs)
#
#     def get(self, request, *args, **kwargs):
#
#         designation = request.user.designation
#         date = request.GET.get('date')
#
#         date = datetime.strptime(date, '%Y-%m-%d').date()
#         office_time = Configuration.objects.filter(designation=designation).first()
#         conference_date = list(Conference.objects.filter(start_date=date).values('start_time', 'end_time'))
#         if not office_time:
#             self.response_format['error'] = 'office time not found'
#             self.response_format['status'] = False
#             return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)
#         office_start = office_time.office_start
#         office_end = office_time.office_end
#
#         start_time = datetime.combine(datetime.today(), office_start)
#         end_time = datetime.combine(datetime.today(), office_end)
#
#         time_slots = []
#         while start_time != end_time:
#
#             slots = {
#                 'start_time': start_time.time()
#             }
#
#             start_time = start_time + timedelta(minutes=15)
#             slots['end_time'] = start_time.time()
#
#             if slots in conference_date:
#                 pass
#             else:
#                 slots['start_time'] = slots['start_time'].strftime('%H:%M')
#                 slots['end_time'] = slots['end_time'].strftime('%H:%M')
#                 time_slots.append(slots)
#
#         self.response_format['data'] = time_slots
#         self.response_format['status'] = True
#         return Response(self.response_format, status=status.HTTP_200_OK)
#
#
# class ConferenceRoomView(viewsets.ModelViewSet):
#     queryset = Conference.objects.all()
#     serializer_class = ConferenceRoomViewSerializer
#     permission_classes = [IsAuthenticated]
#
#     def __init__(self, **kwargs):
#         self.response_format = ResponseFormat().response
#         super().__init__(**kwargs)
#
#     def list(self, request, *args, **kwargs):
#
#         month = int(request.GET.get('month'))
#         year = int(request.GET.get('year'))
#
#         first_day = date(year, month, 1)
#         last_day = date(year, month, calendar.monthrange(year, month)[1])
#
#         queryset = self.queryset.filter(start_date__range=[first_day, last_day])
#
#         serializer = self.get_serializer(queryset, many=True)
#
#         self.response_format['data'] = serializer.data
#         self.response_format['status'] = True
#         return Response(self.response_format, status=status.HTTP_200_OK)
#
#     def create(self, request, *args, **kwargs):
#         data = request.data
#         serializer = self.serializer_class(data=data, context={'user': request.user})
#         if serializer.is_valid(raise_exception=True):
#             serializer.save()
#
#             # self.response_format['data'] = serializer.data
#             self.response_format['message'] = 'Conference data created successfully'
#             self.response_format['status'] = True
#             return Response(self.response_format, status=status.HTTP_201_CREATED)
#
#         self.response_format['data'] = serializer.errors
#         self.response_format['status'] = False
#         return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)
#
#     def update(self, request, *args, **kwargs):
#         data = request.data
#         partial = kwargs.pop('partial', False)
#         instance = self.get_object()
#         serializer = self.serializer_class(data=data, context={'user': request.user}, instance=instance,
#                                            partial=partial)
#         if serializer.is_valid(raise_exception=True):
#             serializer.save()
#             # self.response_format['data'] = serializer.data
#             self.response_format['message'] = 'Conference data Updated successfully'
#             self.response_format['status'] = True
#             return Response(self.response_format, status=status.HTTP_201_CREATED)
#
#         self.response_format['data'] = serializer.errors
#         self.response_format['status'] = False
#         return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)
#
#     def destroy(self, request, *args, **kwargs):
#
#         conference = self.get_object()
#         type = request.query_params['type']
#         event_code = conference.event_code
#
#         start_date = conference.start_date
#         current_date = d1.datetime.now().date()
#         if current_date > start_date:
#             self.response_format['error'] = 'Cannot delete old events!'
#             self.response_format['status'] = False
#             return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)
#
#         if type == 'delete_all':
#             all_delete = Conference.objects.filter(event_code=event_code, start_date__gte=current_date)
#             all_delete.delete()
#         else:
#             single_delete = Conference.objects.filter(event_code=event_code, start_date=start_date)
#             single_delete.delete()
#
#         self.response_format['message'] = 'Conference data deleted successfully'
#         self.response_format['status'] = True
#         return Response(self.response_format, status=status.HTTP_200_OK)
#
#
# class EmployeeViewSet(viewsets.ModelViewSet):
#     # queryset = Employee.objects.all()
#     queryset = CustomUser.objects.all()
#     serializer_class = EmployeeSerializer
#     permission_classes = [IsAuthenticated]
#
#     def __init__(self, **kwargs):
#         self.response_format = ResponseFormat().response
#         super().__init__(**kwargs)
#
#     def create(self, request, *args, **kwargs):
#         data = request.data
#         serializer = self.serializer_class(data=data, context={'user': request.user})
#         if serializer.is_valid(raise_exception=True):
#             serializer.save()
#             self.response_format['data'] = serializer.data
#             self.response_format['message'] = 'Conference data created successfully'
#             self.response_format['status'] = True
#             return Response(self.response_format, status=status.HTTP_201_CREATED)
#
#         self.response_format['data'] = serializer.errors
#         self.response_format['status'] = False
#         return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)
#
#
# class UpcomingConferenceView(views.APIView):
#     queryset = Conference.objects.all().order_by('start_date', 'start_time')
#     serializer_class = UpcomingConferenceSerializer
#     permission_classes = [IsAuthenticated]
#
#     def __init__(self, **kwargs):
#         self.response_format = ResponseFormat().response
#         super().__init__(**kwargs)
#
#     # def get(self, request, *args, **kwargs):
#     #     month = int(request.GET.get('month'))
#     #     year = int(request.GET.get('year'))
#     #
#     #     today = datetime.now().date()
#     #     current_time = datetime.now().time()
#     #     last_day = date(year, month, calendar.monthrange(year, month)[1])
#     #
#     #     queryset = self.queryset.filter(start_date__range=[today, last_day]).exclude(start_date=today, start_time__gt=current_time)
#     #
#     #     serializer = self.serializer_class(queryset, many=True)
#     #
#     #     all_data = serializer.data
#     #
#     #     for index, data in enumerate(all_data):
#     #         data['index'] = index + 1
#     #         # print(data['index'])
#     #
#     #     self.response_format['data'] = all_data
#     #     self.response_format['status'] = True
#     #     return Response(self.response_format, status=status.HTTP_201_CREATED)
#     def get(self, request, *args, **kwargs):
#         month = int(request.GET.get('month'))
#         year = int(request.GET.get('year'))
#
#         today = datetime.now().date()
#         current_time = datetime.now().time()
#         last_day = date(year, month, calendar.monthrange(year, month)[1])
#
#         today_events = self.queryset.filter(
#             start_date=today, start_time__gte=current_time
#         ).order_by('start_time')
#
#         future_events = self.queryset.filter(
#             start_date__range=[today + timedelta(days=1), last_day]
#         ).order_by('start_date', 'start_time')
#
#         queryset = list(today_events) + list(future_events)
#
#         serializer = self.serializer_class(queryset, many=True)
#         all_data = serializer.data
#
#         for index, data in enumerate(all_data):
#             data['index'] = index + 1
#
#         self.response_format['data'] = all_data
#         self.response_format['status'] = True
#         return Response(self.response_format, status=status.HTTP_200_OK)
#
#
# class TopicViewSet(viewsets.ModelViewSet):
#     permission_classes = [IsAuthenticated]
#     queryset = Topic.objects.all()
#     serializer_class = TopicViewSetSerializer
#
#     def __init__(self, **kwargs):
#         self.response_format = ResponseFormat().response
#         super().__init__(**kwargs)
#
#     def create(self, request, *args, **kwargs):
#         serializer = self.serializer_class(data=request.data, context={'user': request.user})
#         if serializer.is_valid(raise_exception=True):
#             serializer.save()
#             self.response_format['data'] = serializer.data
#             self.response_format['message'] = 'Topic created successfully'
#             self.response_format['status'] = True
#             return Response(self.response_format, status=status.HTTP_201_CREATED)
#
#         self.response_format['data'] = serializer.errors
#         self.response_format['status'] = False
#         return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)
#
#     def update(self, request, *args, **kwargs):
#         instance = self.get_object()
#         serializer = self.get_serializer(instance, data=request.data, partial=True, context={'user', request.user})
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#
#         self.response_format['message'] = 'Conference data deleted successfully'
#         self.response_format['status'] = True
#         self.response_format['data'] = serializer.data
#         return Response(self.response_format, status=status.HTTP_200_OK)
#
#
# class getTopPresenter(views.APIView):
#     serializer_class = getTopPresenterSerializer
#     permission_classes = [IsAuthenticated]
#
#     def __init__(self, **kwargs):
#         self.response_format = ResponseFormat().response
#         super().__init__(**kwargs)
#
#     def get(self, request, *args, **kwargs):
#         today_date = d1.datetime.now().date()
#         top_presenters = CustomUser.objects.annotate(
#             num_presented=Count('presenting__start_date', distinct=True,
#                                 filter=Q(presenting__title__isnull=False, presenting__agenda__isnull=False,
#                                          presenting__start_date__isnull=False, presenting__start_date__lt=today_date))
#         ).order_by('-num_presented')[:5]
#
#         serializer = self.serializer_class(top_presenters, many=True)
#
#         self.response_format['status'] = True
#         self.response_format['data'] = serializer.data
#         return Response(self.response_format, status=status.HTTP_200_OK)
#
#
# class getTopTopics(views.APIView):
#     serializer_class = getTopTopicsSerializer
#     permission_classes = [IsAuthenticated]
#
#     def __init__(self, **kwargs):
#         self.response_format = ResponseFormat().response
#         super().__init__(**kwargs)
#
#     def get(self, request, *args, **kwargs):
#         today_date = d1.datetime.now().date()
#         top_topics = Topic.objects.annotate(
#             num_topic=Count('topic__start_date', distinct=True,
#                             filter=Q(topic__title__isnull=False, topic__agenda__isnull=False,
#                                      topic__start_date__isnull=False, topic__start_date__lt=today_date))
#         ).order_by('-num_topic')[:5]
#
#         serializer = self.serializer_class(top_topics, many=True)
#
#         self.response_format['status'] = True
#         self.response_format['data'] = serializer.data
#         return Response(self.response_format, status=status.HTTP_200_OK)
#
#
# def delete_all(request):
#     if request.method == 'GET':
#         Conference.objects.all().delete()
#         return JsonResponse({'message': 'Delete Successfully'}, status=status.HTTP_200_OK)
#     else:
#         return JsonResponse({'error': 'Error Occurred'}, status=status.HTTP_400_BAD_REQUEST)
#
#
# class UserMail(ModelViewSet):
#     serializer_class = UserEmailSerializer
#     permission_classes = [CheckSoftwareUser]
#
#     def __init__(self, **kwargs):
#         self.response_format = ResponseFormat().response
#         super().__init__(**kwargs)
#
#     def list(self, request, *args, **kwargs):
#         mail = request.GET.get('mail')
#         user = CustomUser.objects.filter(email=mail).first()
#         if user:
#             user.is_using_surveillance_software = True
#             user.save()
#             self.response_format['status'] = True
#             self.response_format['data'] = user.email
#             return Response(self.response_format, status=status.HTTP_200_OK)
#         else:
#             self.response_format['status'] = False
#             self.response_format['data'] = 'User Does not exist'
#             return Response(self.response_format, status=status.HTTP_404_NOT_FOUND)
#
