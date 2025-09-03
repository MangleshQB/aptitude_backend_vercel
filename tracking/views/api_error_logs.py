from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from tracking.models import APIErrorLogs
from tracking.serializer import APIErrorLogsSerializer
from utils.views import CustomModelViewSet
from rest_framework.response import Response
from rest_framework import status


class APIErrorLogsViewSet(CustomModelViewSet):
    queryset = APIErrorLogs.objects.filter(is_deleted=False).order_by('-id')
    serializer_class = APIErrorLogsSerializer
    # permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def create(self, request, *args, **kwargs):

        serializer = self.serializer_class(data=request.data,
                                           context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        self.response_format["data"] = serializer.data
        self.response_format["status"] = True
        return Response(self.response_format, status=status.HTTP_200_OK)







