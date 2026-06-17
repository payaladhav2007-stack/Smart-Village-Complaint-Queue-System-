from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('citizen', 'Citizen'),
        ('staff', 'Staff'),
        ('admin', 'Admin'),
    ]

    phone_number = models.CharField(max_length=15, blank=True, null=True)
    ward_number  = models.CharField(max_length=10, blank=True, null=True)
    role         = models.CharField(max_length=10, choices=ROLE_CHOICES, default='citizen')

    def __str__(self):
        return f"{self.username} ({self.role})"