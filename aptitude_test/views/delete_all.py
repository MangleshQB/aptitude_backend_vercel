from django.http import JsonResponse
from rest_framework import status

from aptitude_test.models import Conference


def delete_all(request):
    if request.method == 'GET':
        Conference.objects.all().delete()
        return JsonResponse({'message': 'Delete Successfully'}, status=status.HTTP_200_OK)
    else:
        return JsonResponse({'error': 'Error Occurred'}, status=status.HTTP_400_BAD_REQUEST)
