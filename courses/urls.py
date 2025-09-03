from django.urls import path, include

from .views import CoursesView

urlpatterns = [
    path('', CoursesView.as_view({'get': 'list'}), name='courses'),
    path('<int:pk>/', CoursesView.as_view({'get': 'retrieve'}), name='courses_id')
]