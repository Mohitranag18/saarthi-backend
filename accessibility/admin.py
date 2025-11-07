from django.contrib import admin
from .models import AccessibilityReport, RouteFeedback


@admin.register(AccessibilityReport)
class AccessibilityReportAdmin(admin.ModelAdmin):
    list_display = ['problem_type', 'severity', 'status', 'user', 'created_at']
    list_filter = ['severity', 'status', 'created_at', 'problem_type']
    search_fields = ['problem_type', 'description', 'user__username']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Location', {
            'fields': ('latitude', 'longitude')
        }),
        ('Report Details', {
            'fields': ('problem_type', 'disability_types', 'severity', 'description', 'photo_url')
        }),
        ('Status', {
            'fields': ('status', 'user')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(RouteFeedback)
class RouteFeedbackAdmin(admin.ModelAdmin):
    list_display = ['disability_type', 'rating', 'user', 'created_at']
    list_filter = ['rating', 'disability_type', 'created_at']
    search_fields = ['comment', 'user__username']
    readonly_fields = ['id', 'created_at']