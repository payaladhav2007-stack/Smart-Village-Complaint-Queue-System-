from django.contrib.auth.models import AbstractUser
from django.db import models


# ============================================================
# GS-REG-101: Location Hierarchy Models (Maharashtra LGD data)
# ============================================================

class State(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class District(models.Model):
    name = models.CharField(max_length=100)
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='districts')
    lgd_code = models.CharField(max_length=20, blank=True, default='')

    def __str__(self):
        return self.name


class Taluka(models.Model):
    name = models.CharField(max_length=100)
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='talukas')
    lgd_code = models.CharField(max_length=20, blank=True, default='')

    def __str__(self):
        return self.name


class VillageCity(models.Model):
    name = models.CharField(max_length=150)
    taluka = models.ForeignKey(Taluka, on_delete=models.CASCADE, related_name='villages_cities')
    lgd_code = models.CharField(max_length=20, blank=True, default='')

    def __str__(self):
        return self.name


# ============================================================
# GS-REG-101: Extended CustomUser
# ============================================================

class User(AbstractUser):
    ROLE_CHOICES = [
        ('citizen', 'Citizen'),
        ('staff', 'Staff / Officer'),
        ('sarpanch', 'Sarpanch / Nagarsevak'),
    ]

    APPROVAL_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    phone_number = models.CharField(max_length=15, blank=True, null=True)
    ward_number  = models.CharField(max_length=10, blank=True, null=True)  # now optional
    role         = models.CharField(max_length=10, choices=ROLE_CHOICES, default='citizen')

    # GS-REG-101: New fields for role-based registration
    village_city = models.ForeignKey(
        VillageCity, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='residents'
    )
    identity_document = models.FileField(
        upload_to='identity_documents/', blank=True, null=True
    )
    approval_status = models.CharField(
        max_length=20, choices=APPROVAL_STATUS_CHOICES, default='approved'
    )
    approved_by = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='approved_users'
    )
    supervisor = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='staff_members', limit_choices_to={'role': 'sarpanch'}
    )

    def __str__(self):
        return f"{self.username} ({self.role})"
