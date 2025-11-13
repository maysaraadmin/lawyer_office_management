from django.contrib import admin
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """Admin configuration for the Appointment model."""
    list_display = ('title', 'user', 'start_time', 'end_time', 'status')
    list_filter = ('status', 'start_time', 'end_time')
    search_fields = ('title', 'description', 'user__username')
    date_hierarchy = 'start_time'
    ordering = ('-start_time',)
    
    fieldsets = (
        ('Appointment Details', {
            'fields': ('user', 'title', 'description')
        }),
        ('Timing', {
            'fields': ('start_time', 'end_time', 'status')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
