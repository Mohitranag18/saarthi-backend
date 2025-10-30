from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class AccessibilityReport(models.Model):
    """
    Model for community-submitted accessibility reports
    """
    REPORT_TYPE_CHOICES = (
        ('ramp', 'Accessible Ramp'),
        ('lift', 'Accessible Lift'),
        ('blocked_path', 'Blocked Path'),
        ('no_ramp', 'Missing Ramp'),
        ('broken_lift', 'Broken Lift'),
        ('tactile_path', 'Tactile Paving'),
        ('obstacle', 'Obstacle'),
        ('other', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='accessibility_reports'
    )
    
    report_type = models.CharField(
        max_length=20,
        choices=REPORT_TYPE_CHOICES
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6
    )
    
    address = models.TextField(blank=True, null=True)
    
    photo = models.ImageField(
        upload_to='accessibility_reports/',
        blank=True,
        null=True
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.report_type}"
    
    class Meta:
        db_table = 'accessibility_reports'
        ordering = ['-created_at']


# class EmergencyRequest(models.Model):
#     """
#     Model for emergency volunteer assistance requests
#     """
#     STATUS_CHOICES = (
#         ('pending', 'Pending'),
#         ('volunteer_found', 'Volunteer Found'),
#         ('in_progress', 'In Progress'),
#         ('completed', 'Completed'),
#         ('cancelled', 'Cancelled'),
#     )
    
#     user = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name='emergency_requests'
#     )
    
#     volunteer = models.ForeignKey(
#         User,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name='emergency_assists'
#     )
    
#     latitude = models.DecimalField(
#         max_digits=9,
#         decimal_places=6
#     )
#     longitude = models.DecimalField(
#         max_digits=9,
#         decimal_places=6
#     )
    
#     description = models.TextField(blank=True)
    
#     status = models.CharField(
#         max_length=20,
#         choices=STATUS_CHOICES,
#         default='pending'
#     )
    
#     qr_verified = models.BooleanField(default=False)
    
#     created_at = models.DateTimeField(auto_now_add=True)
#     completed_at = models.DateTimeField(null=True, blank=True)
    
#     def __str__(self):
#         return f"Emergency by {self.user.username} - {self.status}"
    
#     class Meta:
#         db_table = 'emergency_requests'
#         ordering = ['-created_at']