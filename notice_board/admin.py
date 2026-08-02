from django.contrib import admin
from .models import Notice


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ['title', 'posted_by', 'village_city', 'is_pinned', 'created_at']
    list_filter = ['is_pinned', 'village_city', 'posted_by__role']
    search_fields = ['title', 'content', 'posted_by__username']
    ordering = ['-is_pinned', '-created_at']