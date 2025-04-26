from django.db import models
from django.utils import timezone

class Incident(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Not Processed'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    name = models.CharField(max_length=255, unique=True)
    video_file = models.FileField(upload_to='videos/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    processed_at = models.DateTimeField(null=True, blank=True)
    faces_found = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class DetectedFace(models.Model):
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='faces')
    face_image = models.ImageField(upload_to='faces/')
    timestamp = models.FloatField()  # Time in seconds where face was detected
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Face from {self.incident.name} at {self.timestamp}s" 