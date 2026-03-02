from django.urls import path
from .views import (
    CourseListCreateView, CourseDetailView, TeacherCoursesView,
    EnrollmentListCreateView, EnrollmentDetailView
)

urlpatterns = [
    path('', CourseListCreateView.as_view(), name='course-list'),
    path('teacher/', TeacherCoursesView.as_view(), name='teacher-courses'),
    path('<int:pk>/', CourseDetailView.as_view(), name='course-detail'),
    path('enrollments/', EnrollmentListCreateView.as_view(), name='enrollment-list'),
    path('enrollments/<int:pk>/', EnrollmentDetailView.as_view(), name='enrollment-detail'),
]