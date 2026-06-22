from django.db import models
from django.conf import settings


def complaint_media_path(instance, filename):
    # Files stored at: complaints/media/<complaint_id>/<filename>
    return f'complaints/media/{instance.id}/{filename}'


class Complaint(models.Model):
    CATEGORY_CHOICES = [
        ('roads', 'Roads/Potholes'),
        ('sanitation', 'Sanitation/Garbage'),
        ('water', 'Water Supply'),
        ('electricity', 'Electricity'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='complaints'
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES
    )
    description = models.TextField()
    media_path = models.FileField(
        upload_to=complaint_media_path,
        null=True,
        blank=True
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.category} - {self.status}"