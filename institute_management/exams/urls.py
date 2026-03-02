from django.urls import path
from .views import (
    ExamListCreateView, ExamDetailView,
    ResultListCreateView, ResultDetailView, StudentResultsView
)

urlpatterns = [
    path('exams/', ExamListCreateView.as_view(), name='exam-list'),
    path('exams/<int:pk>/', ExamDetailView.as_view(), name='exam-detail'),
    path('results/', ResultListCreateView.as_view(), name='result-list'),
    path('results/<int:pk>/', ResultDetailView.as_view(), name='result-detail'),
    path('students/<int:student_id>/results/', StudentResultsView.as_view(), name='student-results'),
]