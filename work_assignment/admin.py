from django.contrib import admin
from .models import WorkAssignment


@admin.register(WorkAssignment)
class WorkAssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'assigned_by', 'assigned_to', 'status', 'due_date', 'created_at']
    list_filter = ['status', 'assigned_by', 'assigned_to']
    search_fields = ['title', 'description']
    ordering = ['-created_at']