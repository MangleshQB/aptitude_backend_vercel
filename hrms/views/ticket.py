from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Case, When, Value, IntegerField
from hrms.models.ticket import Ticket
from hrms.serializer import TicketSerializer
from utils.common import get_all_reporting_users
from utils.views import CustomModelViewSet

class TicketViewSet(CustomModelViewSet):

        permission_classes = [IsAuthenticated]
        status_order = Case(
                When(status='pending', then=1),
                When(status='in_progress', then=2),
                When(status='resolved', then=3),
                default=Value(4),
                output_field=IntegerField(),
        )

        priority_order = Case(
                When(priorities='High', then=1),
                When(priorities='Medium', then=2),
                When(priorities='Low', then=3),
                default=Value(4),
                output_field=IntegerField(),
        )

        queryset = Ticket.objects.filter(is_deleted=False).order_by(status_order, priority_order, '-id')

        serializer_class =  TicketSerializer

        search_fields = [
                'category__name',
                'sub_category__name',
                'title',
                'description',
                'priorities',
                'status',
                'assigned_to__first_name',
                'assigned_to__last_name',
        ]

        ordering_fields = [
                'category__name',
                'sub_category__name',
                'title',
                'description',
                'priorities',
                'status',
                'assigned_to__first_name',
                'assigned_to__last_name',
        ]

        def create(self, request, *args, **kwargs):
                serializer = self.serializer_class(data=request.data,
                                                   context={'created_by': request.user, 'request': request})
                serializer.is_valid(raise_exception=True)
                serializer.save()
                self.response_format["data"] = serializer.data
                self.response_format["status"] = True
                return Response(self.response_format, status=status.HTTP_200_OK)

        def retrieve(self, request, *args, **kwargs):
                obj = self.get_object()
                serializer = self.serializer_class(instance=obj, context={'request': request})
                self.response_format["data"] = serializer.data
                self.response_format["status"] = True
                if not serializer.data:
                        self.response_format["message"] = "No data found!"
                return Response(self.response_format, status=status.HTTP_200_OK)

        def list(self, request, *args, **kwargs):

                permissions = request.user.groups.all().first().permissions.filter(
                        content_type__model='ticket').values_list('codename', flat=True)

                print(permissions)

                if 'all_ticket' in permissions:

                        self.queryset = Ticket.objects.filter(is_deleted=False).order_by(self.status_order, self.priority_order, '-id')

                elif 'team_ticket' in permissions:

                        team = get_all_reporting_users(request.user)
                        self.queryset = Ticket.objects.filter(Q(is_deleted=False) & (Q(notify_to__in=[request.user]) | Q(created_by__in=team))).distinct().order_by(self.status_order, self.priority_order, '-id')

                elif 'owned_ticket' in permissions:

                        self.queryset = Ticket.objects.filter(
                                Q(is_deleted=False) & (Q(notify_to__in=[request.user]) | Q(created_by=request.user))).distinct().order_by(self.status_order, self.priority_order, '-id')

                else:

                        self.response_format['status'] = False
                        self.response_format['data'] = 'user have no permission'
                        return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)


                if request.GET.get("search", None) or request.GET.get("ordering", None):

                        queryset = self.filter_queryset(self.queryset)
                else:
                        queryset = self.queryset

                page = self.paginate_queryset(queryset)
                if page is not None:
                        serializer = self.get_serializer(page, many=True, context={'request': request})

                        return self.get_paginated_response(serializer.data)

                serializer = self.get_serializer(queryset, many=True)
                self.response_format["data"] = serializer.data
                self.response_format["status"] = True
                if not serializer.data:
                        self.response_format["message"] = "No data found!"
                return Response(self.response_format, status=status.HTTP_200_OK)

        def update(self, request, *args, **kwargs):
                obj = self.get_object()
                serializer = self.serializer_class(instance=obj, data=request.data,
                                                   context={'updated_by': request.user, 'request': request},
                                                   partial=True)
                if serializer.is_valid():
                        serializer.save()
                        self.response_format["data"] = serializer.data
                        self.response_format["status"] = True
                        return Response(self.response_format, status=status.HTTP_200_OK)
                else:
                        self.response_format["data"] = serializer.errors
                        self.response_format["status"] = False
                        self.response_format["error"] = status.HTTP_400_BAD_REQUEST
                        self.response_format["message"] = "Validation failed"
                        return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)

