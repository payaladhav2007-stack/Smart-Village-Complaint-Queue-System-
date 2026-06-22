from django.contrib import admin
from .models import Complaint

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'status', 'latitude', 'longitude', 'created_at']
    list_filter = ['category', 'status']
    search_fields = ['user__username', 'description', 'category']
    ordering = ['-created_at']
