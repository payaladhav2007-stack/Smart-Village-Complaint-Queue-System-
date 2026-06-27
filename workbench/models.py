from django.db import models
from django.conf import settings

class ReassignmentLog(models.Model):

    TICKET_TYPE_CHOICES = [
        ('complaint', 'Complaint'),
        ('appointment', 'Appointment'),
    ]

    ticket_type = models.CharField(
        max_length=20,
        choices=TICKET_TYPE_CHOICES
    )
    ticket_id = models.IntegerField()
    previous_status = models.CharField(max_length=50)
    new_status = models.CharField(max_length=50)
    reassigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reassignments'
    )
    notes = models.TextField(blank=True, default='')
    reassigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-reassigned_at']

    def __str__(self):
        return f"{self.ticket_type} #{self.ticket_id} → {self.new_status} by {self.reassigned_by}"
