import uuid
from django.db import models
from django.conf import settings


class AccessibilityReport(models.Model):
    SEVERITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Resolved', 'Resolved'),
        ('Under Review', 'Under Review'),
        ('Duplicate', 'Duplicate'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    latitude = models.DecimalField(max_digits=9, decimal_places=8)
    longitude = models.DecimalField(max_digits=9, decimal_places=8)
    problem_type = models.CharField(max_length=100)
    disability_types = models.JSONField(default=list)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='Medium')
    description = models.TextField(max_length=200)
    photo_url = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['latitude', 'longitude']),
            models.Index(fields=['severity', 'status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.problem_type} ({self.severity}) - {self.status}"


class RouteFeedback(models.Model):
    RATING_CHOICES = [
        (1, 'Very Poor'),
        (2, 'Poor'),
        (3, 'Average'),
        (4, 'Good'),
        (5, 'Excellent'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    start_lat = models.DecimalField(max_digits=9, decimal_places=6)
    start_lon = models.DecimalField(max_digits=9, decimal_places=6)
    end_lat = models.DecimalField(max_digits=9, decimal_places=6)
    end_lon = models.DecimalField(max_digits=9, decimal_places=6)
    disability_type = models.CharField(max_length=50)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Feedback: {self.rating}/5 - {self.disability_type}"