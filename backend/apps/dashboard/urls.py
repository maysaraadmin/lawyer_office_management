from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Main dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # User profile
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    
    # Statistics and analytics
    path('stats/', views.DashboardStatsView.as_view(), name='dashboard-stats'),
    path('activity-chart/', views.ActivityChartView.as_view(), name='activity-chart'),
    path('client-growth/', views.ClientGrowthView.as_view(), name='client-growth'),
    
    # Recent activities
    path('activities/', views.RecentActivityView.as_view(), name='recent-activities'),
]
