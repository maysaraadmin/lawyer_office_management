from django.contrib import admin
from .models import Case, CaseNote

class CaseNoteInline(admin.StackedInline):
    """Inline admin for CaseNote model."""
    model = CaseNote
    extra = 0
    readonly_fields = ('created_at', 'updated_at')
    fields = ('author', 'content', 'created_at', 'updated_at')

@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    """Admin configuration for the Case model."""
    list_display = ('title', 'client', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('title', 'description', 'client__first_name', 'client__last_name')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Case Information', {
            'fields': ('title', 'description', 'client', 'status')
        }),
        ('Assignment', {
            'fields': ('created_by', 'assigned_to')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'closed_at'),
            'classes': ('collapse',)
        }),
    )
    
    filter_horizontal = ('assigned_to',)
    inlines = [CaseNoteInline]
    readonly_fields = ('created_at', 'updated_at')

@admin.register(CaseNote)
class CaseNoteAdmin(admin.ModelAdmin):
    """Admin configuration for the CaseNote model."""
    list_display = ('case', 'author', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('content', 'case__title', 'author__username')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Note Details', {
            'fields': ('case', 'author', 'content')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
