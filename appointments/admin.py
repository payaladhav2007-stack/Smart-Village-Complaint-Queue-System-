from django.contrib import admin
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'service_type', 'token_number', 'scheduled_time', 'status', 'created_at']
    list_filter = ['service_type', 'status']
    search_fields = ['user__username', 'token_number', 'service_type']
    ordering = ['-scheduled_time']
