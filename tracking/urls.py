from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UserMouseTrackingView, UserScreenshotCountView, UserScreenshotView, MissingScreenshotsView, ScreenshotsView, \
    UserMouseTrackingGETView, CreateLog,UserSoftwareUsageView, GetUserSoftwareUsage, GetUserSoftwareUsageReport, getSoftwareDetails,IdleTimeApprovalViewSet ,APIErrorLogsViewSet
from .views.idle_time_approval import IdleTimeApprovalReasonList

router = DefaultRouter()
router.register('idle_time_approval_request', IdleTimeApprovalViewSet)
router.register('api_error_logs', APIErrorLogsViewSet)


urlpatterns = [
    path('', include(router.urls)),

    path('user_mouse_tracking/', UserMouseTrackingView.as_view(), name='user_mouse_tracking'),
    path('user_mouse_tracking_get/', UserMouseTrackingGETView.as_view(), name='user_mouse_trackingGET'),
    path('screenshot_count/', UserScreenshotView.as_view(), name='screenshot_count'),
    path('user_screenshot/', UserScreenshotCountView.as_view(), name='user_screenshot'),
    path('screenshot/', ScreenshotsView.as_view(), name='screenshots'),
    path('missing_screenshot/', MissingScreenshotsView.as_view(), name='missing_screenshots'),
    path('create_log/', CreateLog.as_view(), name='create_log'),
    path('user_software_usage/', UserSoftwareUsageView.as_view(), name='user_software_usage'),
    path('get_user_software_usage/', GetUserSoftwareUsage.as_view(), name='get_user_software_usage'),
    path('get_user_software_report/', GetUserSoftwareUsageReport.as_view(), name='get_user_software_report'),
    path('get_software_details/', getSoftwareDetails.as_view(), name='get_software_details'),
    path('idle_time_approval_reason_list/', IdleTimeApprovalReasonList.as_view({'get':'list'}), name='idle_time_approval_reason_list'),



]
