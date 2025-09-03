from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import status
from configuration.models import App_Version
from configuration.serializers import AppVersionSerializer
from utils.views import CustomModelViewSet
from rest_framework.viewsets import ModelViewSet

class AppVersionView(ModelViewSet):
    queryset = App_Version.objects.all()
    serializer_class = AppVersionSerializer
    # permission_classes = (AllowAny,)

    def list(self, request, *args, **kwargs):
        os_type = request.GET.get('system_os', 'Windows')
        if os_type:
            if os_type == 'Windows':
                queryset = App_Version.objects.filter(system_os=os_type).order_by('id').last()
            elif os_type == 'Linux':
                queryset = App_Version.objects.filter(system_os=os_type).order_by('id').last()
            elif os_type == 'Mac':
                queryset = App_Version.objects.filter(system_os=os_type).order_by('id').last()
        else:
            queryset = self.queryset.order_by('id').last()

        if not queryset:
            return Response({"detail": "No records found."}, status=404)

        serializer = self.get_serializer(queryset)
        return Response(serializer.data, status=200)

