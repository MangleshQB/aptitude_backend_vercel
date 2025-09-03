from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from hrms.models import KnowledgeBase
from hrms.serializer import KnowledgeBaseSerializer
from utils.views import CustomModelViewSet


class KnowledgeBaseViewSet(CustomModelViewSet):

    queryset = KnowledgeBase.objects.filter(is_deleted=False).order_by('-id')
    serializer_class = KnowledgeBaseSerializer
    permission_classes = [IsAuthenticated]

    search_fields = [
        'title',
        'category__name',
    ]

    ordering_fields = [
        'title',
        'category__name',
    ]

    def list(self, request, *args, **kwargs):
        # permissions = request.user.groups.all().first().permissions.filter(
        #     content_type__model='knowledgebase').values_list('codename', flat=True)

        # code = 'hrms.add_knowledgebase'

        user_permission = request.user.get_group_permissions()
        # print(user_permission)

        # print('CHeck test = ', request.user.has_perm(code))
        #
        # if request.user.has_perm(code):
        #     print('Has Permission')
        # else:
        #     print('Has not Permission', request.user.has_perm(code))

        if all(permission in user_permission for permission in ['hrms.add_knowledgebase', 'hrms.change_knowledgebase', 'hrms.delete_knowledgebase', 'hrms.view_knowledgebase']):
            self.queryset = KnowledgeBase.objects.filter(is_deleted=False).order_by('-id')
        else:
            self.queryset = KnowledgeBase.objects.filter(is_deleted=False,
                                                         designation=request.user.designation).order_by('-id')

        if request.GET.get("search", None) or request.GET.get("ordering", None):
            queryset = self.filter_queryset(self.get_queryset())
        else:
            queryset = self.get_queryset()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)

            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        self.response_format["data"] = serializer.data
        self.response_format["status"] = True
        if not serializer.data:
            self.response_format["message"] = "No data found!"
        return Response(self.response_format, status=status.HTTP_200_OK)


    # def create(self, request, *args, **kwargs):
    #     serializer = self.serializer_class(data=request.data,
    #                                        context={'created_by': request.user})
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     self.response_format["data"] = serializer.data
    #     self.response_format["status"] = True
    #     return Response(self.response_format, status=status.HTTP_200_OK)
