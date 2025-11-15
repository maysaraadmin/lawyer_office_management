from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class DashboardStats(models.Model):
    """Model for storing cached dashboard statistics"""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='dashboard_stats'
    )
    stat_date = models.DateField(auto_now_add=True)
    total_clients = models.IntegerField(default=0)
    total_appointments = models.IntegerField(default=0)
    upcoming_appointments = models.IntegerField(default=0)
    completed_appointments = models.IntegerField(default=0)
    cancelled_appointments = models.IntegerField(default=0)
    new_clients_this_month = models.IntegerField(default=0)
    revenue_this_month = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        unique_together = ['user', 'stat_date']
        ordering = ['-stat_date']
    
    def __str__(self):
        return f"{self.user.email} - {self.stat_date}"


class RecentActivity(models.Model):
    """Model for tracking recent user activities"""
    
    ACTION_TYPES = (
        ('client_created', 'Client Created'),
        ('client_updated', 'Client Updated'),
        ('appointment_created', 'Appointment Created'),
        ('appointment_updated', 'Appointment Updated'),
        ('appointment_completed', 'Appointment Completed'),
        ('appointment_cancelled', 'Appointment Cancelled'),
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recent_activities'
    )
    action_type = models.CharField(max_length=25, choices=ACTION_TYPES)
    description = models.CharField(max_length=255)
    related_object_id = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.action_type}"
