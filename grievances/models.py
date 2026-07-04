from django.db import models
from django.conf import settings


def complaint_media_path(instance, filename):
    # Files stored at: complaints/media/<complaint_id>/<filename>
    return f'complaints/media/{instance.id}/{filename}'

MAIN_CATEGORY_CHOICES = [
    ('government', 'Government Services'),
    ('personal', 'Personal Issues'),
    ('other', 'Other'),
]

GOVERNMENT_SUB_CHOICES = [
    ('roads', 'Roads & Potholes'),
    ('water', 'Water Supply & Pipeline'),
    ('electricity', 'Electricity & Street Lights'),
    ('sanitation', 'Sanitation & Garbage'),
    ('property_damage', 'Public Property Damage'),
    ('drainage', 'Drainage & Flooding'),
    ('tree', 'Tree Fallen / Obstruction'),
    ('stray_animals', 'Stray Animal Issues'),
    ('internet', 'Internet & Connectivity'),
    ('health', 'Public Health & Sanitation'),
    ('education', 'School & Education Infrastructure'),
    ('transport', 'Public Transport Issues'),
]

PERSONAL_SUB_CHOICES = [
    ('family_dispute', 'Family Dispute'),
    ('property_dispute', 'Property Dispute'),
    ('neighbour_water', 'Neighbour Water Issue'),
    ('noise', 'Noise Complaint'),
    ('housing', 'Housing & Shelter'),
    ('employment', 'Employment Issue'),
    ('document_delay', 'Document & Certificate Delay'),
    ('financial_fraud', 'Financial Fraud'),
]

class Complaint(models.Model):
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
    main_category = models.CharField(
        max_length=20,
        choices=MAIN_CATEGORY_CHOICES,
        default='government'
    )
    sub_category = models.CharField(
        max_length=50,
        blank=True,
        default=''
    )
    complaint_subject = models.CharField(
        max_length=200,
        blank=True,
        default=''
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
        return f"{self.user.username} - {self.main_category} - {self.sub_category} - {self.status}"
