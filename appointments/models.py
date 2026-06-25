from django.db import models
from django.conf import settings

class Appointment(models.Model):

    SERVICE_TYPE_CHOICES = [
        ('birth_certificate', 'Birth Certificate'),
        ('death_certificate', 'Death Certificate'),
        ('income_certificate', 'Income Certificate'),
        ('residence_certificate', 'Residence Certificate'),
        ('caste_certificate', 'Caste Certificate'),
        ('property_certificate', 'Property Certificate'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    service_type = models.CharField(
        max_length=50,
        choices=SERVICE_TYPE_CHOICES
    )
    token_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True
    )
    scheduled_time = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    form_data_jsonb = models.JSONField(
        default=dict,
        blank=True,
        help_text='Dynamic certificate form fields stored as JSONB'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-scheduled_time']

    def __str__(self):
        return f"{self.user.username} - {self.service_type} - Token: {self.token_number}"
