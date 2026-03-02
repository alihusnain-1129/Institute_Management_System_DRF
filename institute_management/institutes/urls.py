from django.urls import path
from .views import InstituteListView, InstituteDetailView, InstituteUpdateView, PendingInstitutesView, ApproveInstituteView

urlpatterns = [
    path('', InstituteListView.as_view(), name='institute-list'),
    path('pending/', PendingInstitutesView.as_view(), name='pending-institutes'),
    path('<int:pk>/', InstituteDetailView.as_view(), name='institute-detail'),
    path('<int:pk>/update/', InstituteUpdateView.as_view(), name='institute-update'),
    path('approve/', ApproveInstituteView.as_view(), name='approve-institute'),
]