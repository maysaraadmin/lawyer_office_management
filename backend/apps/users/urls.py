from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

# Use a unique namespace for the users app
app_name = 'users_api'

urlpatterns = [
    # Authentication
    path('login/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.RegisterView.as_view(), name='register'),
    
    # User management
    path('users/', views.UserListCreateView.as_view(), name='user-list'),
    path('users/<str:id>/', views.UserDetailView.as_view(), name='user-detail'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
]
