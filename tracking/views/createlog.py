from datetime import datetime

from django.http import JsonResponse
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from tracking.models import RestartLogs

class CreateLog(APIView):

    # permission_classes = (IsAuthenticated,)
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        user = request.user
        description = request.query_params.get('description', '')

        logs = RestartLogs.objects.filter(user=user, created_at__date=datetime.now().date())
        response_data = {}
        if logs: 
            RestartLogs.objects.create(user=user, status=RestartLogs.RESTARTED, created_by=user, description=description)
            response_data['message'] = 'Restart Successful'
        else:
            RestartLogs.objects.create(user=user, status=RestartLogs.STARTED, created_by=user, description=description)
            response_data['message'] = 'Start Successful'

        return JsonResponse(response_data, status=status.HTTP_200_OK)


