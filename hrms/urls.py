from django.urls import path, include
from rest_framework.routers import DefaultRouter
# from .views import  HolidayView
from .views import TicketViewSet, KnowledgeBaseCategoryViewSet
from .views.knowledge_base import KnowledgeBaseViewSet
from .views.leave import LeaveViewSet

router = DefaultRouter()
router.register('ticket', TicketViewSet)
router.register('knowledgebase', KnowledgeBaseViewSet)
router.register('leave', LeaveViewSet)
router.register('knowledgebase_category', KnowledgeBaseCategoryViewSet)



urlpatterns = [
    path('', include(router.urls)),
    # path('knowledgebase_category/', KnowledgeBaseCategoryViewSet.as_view({'get':'list','create':'create'}), name='knowledgebase_category'),
]