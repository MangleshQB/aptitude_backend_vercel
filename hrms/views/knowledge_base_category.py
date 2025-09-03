from rest_framework.permissions import IsAuthenticated

from hrms.models import KnowledgeBaseCategory
from hrms.serializer import KnowledgeBaseCategorySerializer
from utils.views import CustomModelViewSet

class KnowledgeBaseCategoryViewSet(CustomModelViewSet):

    queryset = KnowledgeBaseCategory.objects.filter(is_deleted=False).order_by('-id')
    serializer_class = KnowledgeBaseCategorySerializer
    permission_classes = [IsAuthenticated]
