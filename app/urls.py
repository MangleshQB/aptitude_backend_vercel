from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import LoginView, TokenVerifyView, GroupsView, PermissionsView, UserView, CheckExistUsername, \
    UserPermissionView, ActiveInactiveCountView, WorkingHoursCalculating, PunchLogs, ExportExcel, UserReporting, \
    ExportReport, UpcomingEmployeesBirthday, UpcomingEmployeesWorkAnniversary, UpcomingThisMonthHoliday
from .views.user_list_view import UserListView
from .views.user_view import ActivateAllUsers

router = DefaultRouter()
router.register(r'user', UserView)
router.register(r'group', GroupsView)
router.register(r'count', ActiveInactiveCountView, basename='count')

urlpatterns = [
    # path('user/', UserView.as_view({'get': 'list'}))
    # path('token/', include(router.urls)),
    # path('group/', GroupsView.as_view({'get': 'list'})),
    path('login_view/', LoginView.as_view(), name='login'),
    path('verify/', TokenVerifyView.as_view()),
    path('permission/', PermissionsView.as_view({'get': 'list'})),
    path('', include(router.urls)),
    path('userlist/', UserListView.as_view({'get': 'list'})),
    path('check_username/', CheckExistUsername.as_view(), name='check_username'),
    path('user_permission/', UserPermissionView.as_view(), name='user_permission'),
    path('activate_all_users/', ActivateAllUsers.as_view(), name='activate_all_users'),
    path('working_hours/', WorkingHoursCalculating.as_view(), name='working_hours'),
    path('punch_log/', PunchLogs.as_view(), name='punch_log'),
    path('export_excel/', ExportExcel.as_view(), name='export_excel'),
    path('export_report/', ExportReport.as_view(), name='export_report'),
    path('screenshot_user_count/', UserReporting.as_view({'get': 'list'}), name='screenshot_user_count'),
    path('upcoming_birthdays/', UpcomingEmployeesBirthday.as_view(), name='upcoming_birthdays'),
    path('upcoming_work_anniversary/', UpcomingEmployeesWorkAnniversary.as_view(), name='upcoming_work_anniversary'),
    path('upcoming_holidays/', UpcomingThisMonthHoliday.as_view(), name='upcoming_holidays'),
]
