from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from app.models import Designation
from app.serializers import DesignationSerializer


class DesignationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    queryset = Designation.objects.all()
    serializer_class = DesignationSerializer
