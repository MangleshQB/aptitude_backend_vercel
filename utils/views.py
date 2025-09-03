from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, status, serializers
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.viewsets import ModelViewSet

from utils.common import ResponseFormat, SetPagination


class DefaultSerializer(serializers.Serializer):
    pass


class CustomModelViewSet(ModelViewSet):

    def __init__(self, **kwargs):
        self.response_format = ResponseFormat().response
        super(CustomModelViewSet, self).__init__(**kwargs)

    queryset = None
    serializer_class = DefaultSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = SetPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    parser_classes = (FormParser, MultiPartParser, JSONParser)
    search_fields = []
    ordering_field = ()
    filter_mapper = dict()

    def list(self, request, *args, **kwargs):
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
        return Response(self.response_format, status=HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.serializer_class(instance=obj)
        self.response_format["data"] = serializer.data
        self.response_format["status"] = True
        if not serializer.data:
            self.response_format["message"] = "No data found!"
        return Response(self.response_format, status=HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'created_by': request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        self.response_format["data"] = serializer.data
        self.response_format["status"] = True
        return Response(self.response_format, status=HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.serializer_class(instance=obj, data=request.data, context={'updated_by': request.user},
                                           partial=True)
        if serializer.is_valid():
            serializer.save()
            self.response_format["data"] = serializer.data
            self.response_format["status"] = True
            return Response(self.response_format, status=HTTP_200_OK)
        else:
            self.response_format["data"] = serializer.errors
            self.response_format["status"] = False
            self.response_format["error"] = HTTP_400_BAD_REQUEST
            self.response_format["message"] = "Validation failed"
            return Response(self.response_format, status=HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        try:
            obj.soft_delete()
            return Response(self.response_format, status=HTTP_200_OK)
        except Exception as e:
            print('Error = ', e)
            self.response_format["status"] = False
            self.response_format["error"] = HTTP_400_BAD_REQUEST
            self.response_format["message"] = "Deletion failed"
            return Response(self.response_format, status=HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["POST"], name="Set Filters")
    def search_filter(self, request, *args, **kwargs):
        try:
            kwargs = {}
            exclude_kwargs = {}
            for key, value in request.data.items():
                if value:
                    f_key = [i for i in self.search_fields if key == i]
                    if not f_key:
                        if key in self.filter_mapper.keys():
                            f_key = [self.filter_mapper[key]]
                        else:
                            f_key = [i for i in self.search_fields if key in i]
                    if value == "-":
                        kwargs[f"{key}"] = None
                    elif "is_" in key:
                        kwargs[f"{key}"] = value
                    elif "~" in str(value):
                        exclude_kwargs[f"{f_key[0]}"] = value.replace("~", "").strip()
                    else:
                        kwargs[f"{f_key[0]}__icontains"] = value

            queryset = self.get_queryset().filter(**kwargs).exclude(**exclude_kwargs)

        except Exception as e:
            self.response_format["data"] = []
            self.response_format["status"] = False
            self.response_format["message"] = "Key is Invalid"
            return Response(self.response_format, status.HTTP_400_BAD_REQUEST)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        self.response_format["data"] = serializer.data
        if not serializer.data:
            self.response_format["message"] = "No Record Found!"
        return Response(self.response_format)

    @swagger_auto_schema(
        method="post",
        request_body=serializer_class(many=True),
        # responses=serializer_class(many=True)
    )
    @action(detail=False, methods=["POST"], name="Create Multiple")
    def create_multiple(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'created_by': request.user}, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        self.response_format["data"] = serializer.data
        self.response_format["status"] = True
        return Response(self.response_format, status=HTTP_200_OK)

    @swagger_auto_schema(
        method="post",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "ids": openapi.Schema(
                    type=openapi.TYPE_ARRAY, description="List of IDs",
                    items=openapi.Schema(type=openapi.TYPE_INTEGER)
                ),
            },
            required=['ids'],
        ),
        responses={status.HTTP_200_OK: 'Deleted Successfully!'},
    )
    @action(detail=False, methods=["POST"], name="Delete Multiple")
    def delete_multiple(self, request, *args, **kwargs):
        if 'ids' not in request.data:
            self.response_format["message"] = "Need list of IDs"
            self.response_format["data"] = []
            self.response_format["status"] = False
            self.response_format["error"] = status.HTTP_400_BAD_REQUEST
            return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)
        count = 0
        error_detail = []
        for ID in request.data["ids"]:
            try:
                queryset = self.get_queryset().get(id=ID)
                queryset.soft_delete()
                count += 1
            except Exception as e:
                error_detail.append(f"{ID} - Object Not Found")
        self.response_format["data"] = (
            "Success" if len(request.data["ids"]) == count else "Error"
        )
        self.response_format["data"] = error_detail
        self.response_format["status"] = True if len(request.data["ids"]) == count else False
        return Response(self.response_format)

    @swagger_auto_schema(
        method="get",
        responses={status.HTTP_200_OK: "Success"},
    )
    @action(detail=False, methods=["GET"], name="Get All")
    def fetch_all(self, request, *args, **kwargs):
        queryset = self.get_queryset().all()
        serializer = self.get_serializer(queryset, many=True)
        self.response_format["count"] = len(serializer.data)
        self.response_format["data"] = serializer.data
        self.response_format["status"] = True
        if not serializer.data:
            self.response_format["message"] = "No Record Found!"
        return Response(self.response_format, status=status.HTTP_200_OK)

    class Meta:
        abstract = True