from django.urls import path, include
from rest_framework.routers import DefaultRouter

from payroll.views import SalarySlipViewSet

router = DefaultRouter()
router.register('salary_slip', SalarySlipViewSet)

urlpatterns = [
    path('', include(router.urls)),

    # path('salary_slip/', SalarySlipViewSet.as_view(), name='salary_slip'),

]