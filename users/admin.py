from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'user_type', 'disability_type', 'is_volunteer_active']
    list_filter = ['user_type', 'disability_type', 'is_volunteer_active']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Saarthi Info', {
            'fields': (
                'user_type', 'phone_number', 'disability_type',
                'needs_wheelchair_access', 'needs_tactile_paths',
                'needs_audio_guidance', 'profile_picture'
            )
        }),
        ('Volunteer Info', {
            'fields': (
                'is_volunteer_active', 'volunteer_rating',
                'volunteer_points', 'volunteer_qr_code'
            )
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Saarthi Info', {
            'fields': ('user_type', 'phone_number', 'disability_type')
        }),
    )