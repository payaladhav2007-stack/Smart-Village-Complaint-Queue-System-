from django.db import models
from django.conf import settings
from grievances.models import Complaint


class WorkAssignment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assignments_created',
        limit_choices_to={'role': 'sarpanch'}
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assignments_received',
        limit_choices_to={'role': 'staff'}
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    related_complaint = models.ForeignKey(
        Complaint,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='work_assignments'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} → {self.assigned_to.username} (by {self.assigned_by.username})"