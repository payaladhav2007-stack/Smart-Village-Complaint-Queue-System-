from django.contrib import admin
from .models import Complaint

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'main_category', 'sub_category', 'complaint_subject', 'status', 'created_at']
    list_filter = ['main_category', 'status']
    search_fields = ['user__username', 'description', 'complaint_subject', 'sub_category']
    ordering = ['-created_at']
