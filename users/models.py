from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom User model for Saarthi app
    """
    USER_TYPE_CHOICES = (
        ('user', 'User'),
        ('volunteer', 'Volunteer'),
    )
    
    DISABILITY_TYPE_CHOICES = (
        ('none', 'None'),
        ('visual', 'Visual Impairment'),
        ('mobility', 'Mobility Impairment'),
        ('hearing', 'Hearing Impairment'),
        ('other', 'Other'),
    )
    
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='user'
    )
    
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )
    
    disability_type = models.CharField(
        max_length=20,
        choices=DISABILITY_TYPE_CHOICES,
        default='none'
    )
    
    needs_wheelchair_access = models.BooleanField(default=False)
    needs_tactile_paths = models.BooleanField(default=False)
    needs_audio_guidance = models.BooleanField(default=False)
    
    # Volunteer specific fields
    is_volunteer_active = models.BooleanField(default=False)
    volunteer_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.0
    )
    volunteer_points = models.IntegerField(default=0)
    
    # QR Code for volunteer verification
    volunteer_qr_code = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=True
    )
    
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        blank=True,
        null=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.username} ({self.user_type})"
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'