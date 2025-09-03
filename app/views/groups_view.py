from rest_framework import status, views, permissions, serializers, filters
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from django.contrib.auth.models import Group, Permission
from app.serializers import GroupSerializer
from utils.common import ResponseFormat
from utils.views import CustomModelViewSet


class GroupsView(CustomModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def __init__(self, **kwargs):
        self.response_format = ResponseFormat().response
        super().__init__(**kwargs)

    def create(self, request, *args, **kwargs):

        data = request.data
        group_name = data.get('name', None)

        if group_name:
            group = Group.objects.filter(name__icontains=group_name).exists()

            if group:
                self.response_format['status'] = False
                self.response_format['message'] = 'Group Name already exists'
                return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data, context={'updated_by': request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        self.response_format['status'] = True
        self.response_format['message'] = 'Group Created Successfully'
        self.response_format['data'] = serializer.data
        return Response(self.response_format, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):

        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        all_data = serializer.data

        for index, data in enumerate(all_data):
            data['index'] = index + 1

        self.response_format['status'] = True
        self.response_format['data'] = all_data
        return Response(self.response_format, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):

        data = request.data
        group_name = data.get('name', None)
        instance = self.get_object()

        if group_name:
            group = Group.objects.filter(name__icontains=group_name).exists()

            if group and instance.name != group_name:
                self.response_format['status'] = False
                self.response_format['message'] = 'Group Name already exists'
                return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(instance, data=request.data, partial=True,context={'updated_by': request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        self.response_format['status'] = True
        self.response_format['message'] = 'Group Updated Successfully'
        self.response_format['data'] = serializer.data
        return Response(self.response_format, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        try:
            obj.delete()
            return Response(self.response_format, status=status.HTTP_200_OK)
        except Exception as e:
            print('Error = ', e)
            self.response_format["status"] = False
            self.response_format["error"] =status.HTTP_400_BAD_REQUEST
            self.response_format["message"] = "Deletion failed"
            return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)

