from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator, MaxValueValidator


class Feedback(models.Model):
    # Polymorphic generic relation fields
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        db_index=True
    )
    target_object_id = models.PositiveIntegerField(
        db_index=True
    )
    target = GenericForeignKey('content_type', 'target_object_id')

    # Feedback fields
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='feedbacks'
    )
    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )
    comment = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(
                fields=['content_type', 'target_object_id'],
                name='feedback_generic_fk_idx'
            ),
        ]
        unique_together = ['content_type', 'target_object_id', 'submitted_by']

    def __str__(self):
        return f"{self.submitted_by.username} rated {self.content_type} #{self.target_object_id} — {self.rating}★"