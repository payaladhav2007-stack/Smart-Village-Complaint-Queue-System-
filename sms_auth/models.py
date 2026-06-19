import random
from datetime import timedelta
from django.db import models
from django.utils import timezone


class SmsOtp(models.Model):
    phone_number = models.CharField(max_length=15)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    @staticmethod
    def generate_code():
        return str(random.randint(100000, 999999))

    def is_valid(self, code):
        return (
            not self.is_used
            and self.code == code
            and timezone.now() <= self.expires_at
        )

    def __str__(self):
        return f"{self.phone_number} - {self.code}"
