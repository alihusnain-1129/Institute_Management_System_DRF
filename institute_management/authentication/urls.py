from django.urls import path
from .views import UserRegistrationView, LoginView, PendingApprovalsView, ApproveUserView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('pending-approvals/', PendingApprovalsView.as_view(), name='pending_approvals'),
    path('approve-user/', ApproveUserView.as_view(), name='approve_user'),
]