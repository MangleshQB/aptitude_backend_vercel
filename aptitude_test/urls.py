from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CreateQuestion, TestPaperListView, RandomQuestion, ConfigurationView, \
    TestPaperUpdate, TimeSlotsView, ConferenceRoomView, delete_all, UpcomingConferenceView, getTopPresenter, \
    getTopTopics, UserMail

from aptitude_test.views import QuestionViewSet, ConferenceRoomView, EmployeeViewSet, TopicViewSet
from app.views import DesignationViewSet

router = DefaultRouter()
router.register(r'questions', QuestionViewSet)
router.register(r'designation', DesignationViewSet)
router.register(r'conference_room', ConferenceRoomView)
router.register(r'employees', EmployeeViewSet)
router.register(r'topic', TopicViewSet)
# router.register('holiday', HolidayView)


urlpatterns = [
    path('create_question/', CreateQuestion.as_view(), name='create_question'),
    path('test_paper/', TestPaperListView.as_view(), name='Test_Paper_List'),
    path('random_question/', RandomQuestion.as_view(), name='Random_Question'),
    path('configuration/', ConfigurationView.as_view({'get': 'list', 'put': 'update'}), name='configuration'),
    path('test_paper_update/', TestPaperUpdate.as_view(), name='Test_Paper_Update'),
    path('time_slots/', TimeSlotsView.as_view(), name='Time_Slots'),
    path('upcoming_conference/', UpcomingConferenceView.as_view(), name='upcoming_conference'),
    path('top_presenter/', getTopPresenter.as_view(), name='top_presenter'),
    path('top_topics/', getTopTopics.as_view(), name='top_topics'),
    path('delete_all/', delete_all),
    path('user_mail/', UserMail.as_view({'get': 'list'})),
    # path('holiday/', HolidayView.as_view({'get': 'list'}), name='holiday'),
    path('', include(router.urls)),
]
