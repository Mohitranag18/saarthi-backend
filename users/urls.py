from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    UserRegistrationView,
    UserProfileView,
    UserDetailView,
    VolunteerToggleActiveView,
)

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', UserRegistrationView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User profile endpoints
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    
    # Volunteer endpoints
    path('volunteer/toggle-active/', VolunteerToggleActiveView.as_view(), name='volunteer-toggle-active'),
]