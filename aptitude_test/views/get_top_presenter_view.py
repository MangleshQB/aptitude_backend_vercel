from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, views, permissions

from aptitude_test.serializers import getTopPresenterSerializer
from utils.common import ResponseFormat
from app.models import CustomUser
import datetime as d1
from django.db.models import Q, Count, F


class getTopPresenter(views.APIView):
    serializer_class = getTopPresenterSerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        self.response_format = ResponseFormat().response
        super().__init__(**kwargs)

    def get(self, request, *args, **kwargs):
        today_date = d1.datetime.now().date()
        top_presenters = CustomUser.objects.annotate(
            num_presented=Count('presenting__start_date', distinct=True,
                                filter=Q(presenting__title__isnull=False, presenting__agenda__isnull=False,
                                         presenting__start_date__isnull=False, presenting__start_date__lt=today_date))
        ).order_by('-num_presented')[:5]

        serializer = self.serializer_class(top_presenters, many=True)

        self.response_format['status'] = True
        self.response_format['data'] = serializer.data
        return Response(self.response_format, status=status.HTTP_200_OK)
