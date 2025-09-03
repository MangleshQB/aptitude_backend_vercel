from django.urls import path, include
from rest_framework.routers import DefaultRouter

# from .views import  HolidayView
from .views import ConfigurationViewAptitude, ConfigurationViewSurveillance, HolidayViewSet, LeaveBalanceViewSet, LeaveTypeViewSet, UserAppVersionView
from .views import AppVersionView, TicketCategoryView
from .views.software_process import SoftwareProcessView

router = DefaultRouter()
router.register('app_version', AppVersionView)
router.register('holidays', HolidayViewSet)
# router.register('leave', LeaveViewSet)
router.register('leave_types', LeaveTypeViewSet)
router.register('ticket_category', TicketCategoryView)


urlpatterns = [
    path('', include(router.urls)),
    path('aptitude_configuration/', ConfigurationViewAptitude.as_view({'get': 'list', 'put': 'update'}), name='configuration_aptitude'),
    path('software_process/',SoftwareProcessView.as_view({'get': 'list'})),
    path('software_configuration/', ConfigurationViewSurveillance.as_view({'get': 'list'}), name='configuration_software'),
    path('leave_balance/', LeaveBalanceViewSet.as_view(), name='leave_balance'),
    path('userapp_version/',UserAppVersionView.as_view(), name='userapp_version'),

]
