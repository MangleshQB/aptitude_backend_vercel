from django.db.models import Sum

from .user_mouse_tracking import UserMouseTrackingView
from .user_screenshot import UserScreenshotView
from .user_screenshot_count import UserScreenshotCountView
from .createlog import CreateLog
from .user_software_usage import UserSoftwareUsageView
from .missing_screenshot_update import MissingScreenshotsView
from .screenshot_post import ScreenshotsView
from .user_mouse_tracking import UserMouseTrackingGETView
from .createlog import CreateLog
from .user_software_usage import UserSoftwareUsageView, GetUserSoftwareUsage, GetUserSoftwareUsageReport, getSoftwareDetails
from .idle_time_approval import IdleTimeApprovalViewSet
from  .api_error_logs import APIErrorLogsViewSet


# from datetime import datetime
#
# from ..models import UserMouseTracking, IdleTimeApproval
#
# mouse_track = UserMouseTracking.objects.filter(user__email='manglesh@quantumbot.co.in',
#                                                                    created_at__date=datetime.now().date()).aggregate(Sum('idle_time'))
# print(mouse_track)
#
# approval = IdleTimeApproval.objects.filter(created_at__date=datetime.now().date(),ref_idle_time__user__email='manglesh@quantumbot.co.in', status=IdleTimeApproval.approved).aggregate(Sum('idle_time'))
# print(approval)
