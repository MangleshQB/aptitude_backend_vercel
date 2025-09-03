from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, views, permissions

from aptitude_test.models import Topic
from aptitude_test.serializers import getTopTopicsSerializer
from utils.common import ResponseFormat
import datetime as d1
from django.db.models import Q, Count, F


class getTopTopics(views.APIView):
    serializer_class = getTopTopicsSerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        self.response_format = ResponseFormat().response
        super().__init__(**kwargs)

    def get(self, request, *args, **kwargs):
        today_date = d1.datetime.now().date()
        top_topics = Topic.objects.annotate(
            num_topic=Count('topic__start_date', distinct=True,
                            filter=Q(topic__title__isnull=False, topic__agenda__isnull=False,
                                     topic__start_date__isnull=False, topic__start_date__lt=today_date))
        ).order_by('-num_topic')[:5]

        serializer = self.serializer_class(top_topics, many=True)

        self.response_format['status'] = True
        self.response_format['data'] = serializer.data
        return Response(self.response_format, status=status.HTTP_200_OK)
