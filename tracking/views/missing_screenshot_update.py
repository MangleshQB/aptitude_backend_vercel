from rest_framework import status
from rest_framework.views import APIView
from django.utils import timezone
from rest_framework.response import Response
from app.models import CustomUser
from tracking.models import UserScreenshots


class MissingScreenshotsView(APIView):

    def get(self, request):
        one_hour_ago = timezone.now() - timezone.timedelta(minutes=30)

        users_with_recent_screenshots = UserScreenshots.objects.filter(created_at__gte=one_hour_ago).values_list('user',flat=True)

        users_without_recent_screenshots = CustomUser.objects.exclude(id__in=users_with_recent_screenshots)

        CustomUser.objects.filter(id__in=users_with_recent_screenshots).update(is_screenshot_active=True)

        users_without_recent_screenshots.update(is_screenshot_active=False)

        users_data = [{"id": user.id, "username": user.username} for user in users_without_recent_screenshots]

        return Response(users_data, status=status.HTTP_200_OK)
