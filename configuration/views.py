# from django.shortcuts import render
# from rest_framework.authentication import TokenAuthentication
# from rest_framework.filters import SearchFilter
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.viewsets import ModelViewSet
# from rest_framework.response import Response
# from rest_framework.views import status
# from configuration.models import App_Version
# from configuration.serializers import AppVersionSerializer
#
#
# # from aptitude_test.views import Pagination
# # from configuration.models.configuration import Holiday
# # from configuration.serializers import HolidaySerializer
# #
# #
# # # Create your views here.
# #
# # class HolidayView(ModelViewSet):
# #     queryset = Holiday.objects.all()
# #     permission_classes = [IsAuthenticated]
# #     serializer_class = HolidaySerializer
# #     pagination_class = Pagination
# #     filter_backends = [SearchFilter]
# #     search_fields = ['name',]
#
# class AppVersionView(ModelViewSet):
#     queryset = App_Version.objects.all()
#     permission_classes = [IsAuthenticated]
#     authentication_classes = [TokenAuthentication]
#     serializer_class = AppVersionSerializer
#
#     def list(self, request, *args, **kwargs):
#         latest_version = self.queryset.order_by('-created_at').first()
#         if latest_version:
#             serializer = self.get_serializer(latest_version)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         else:
#             return Response({"detail": "No app versions available"}, status=status.HTTP_404_NOT_FOUND)
#
