from django.contrib import admin
from .models import Feedback

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['submitted_by', 'content_type', 'target_object_id', 'rating', 'comment', 'created_at']
    list_filter = ['content_type', 'rating']
    search_fields = ['submitted_by__username', 'comment']
    ordering = ['-created_at']
