# from django.db import models
from django.contrib.gis.db import models
from django.contrib.auth import get_user_model

User = get_user_model()
# Create your models here.

class EmergencyRequests(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('volunteer_found', 'Volunteer Found'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='emergency_request'
    )
    volunteer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='emergency_assists'
    )
    #ai made this 

    location = models.PointField(geography=True, srid=4326) 
    description = models.TextField(blank=True)
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    qr_verified = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Emergency by {self.user.username} - {self.status}"
    
    class Meta:
        db_table = 'emergency_requests'
        ordering = ['-created_at']
    
class VolunteerLocations(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='volunteer'
    )
    location = models.PointField(geography=True, srid=4326) 
    created_at = models.DateTimeField(auto_now_add=True)

    class  Meta:
        db_table='volunteer_location'
        ordering=['-created_at']