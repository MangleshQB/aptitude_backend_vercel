from rest_framework.permissions import IsAuthenticated
from configuration.models import TicketCategory
from configuration.serializers import TicketCategorySerializer
from utils.views import CustomModelViewSet

class TicketCategoryView(CustomModelViewSet):
    queryset = TicketCategory.objects.filter(is_deleted=False).order_by('-id')
    serializer_class = TicketCategorySerializer
    permission_classes = (IsAuthenticated,)

    search_fields = [
        'name',
        'category__name'
    ]

    ordering_field = [
        'name',
        'category__name'
    ]
