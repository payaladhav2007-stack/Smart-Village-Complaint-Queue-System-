from django.db import models
from django.conf import settings
from accounts.models import VillageCity


class Notice(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notices'
    )
    village_city = models.ForeignKey(
        VillageCity,
        on_delete=models.CASCADE,
        related_name='notices'
    )
    is_pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return f"{self.title} — {self.posted_by.username} ({self.village_city.name})"