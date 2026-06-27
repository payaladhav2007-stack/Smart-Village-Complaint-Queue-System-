from django.contrib import admin
from .models import ReassignmentLog

@admin.register(ReassignmentLog)
class ReassignmentLogAdmin(admin.ModelAdmin):
    list_display = ['ticket_type', 'ticket_id', 'previous_status', 'new_status', 'reassigned_by', 'reassigned_at']
    list_filter = ['ticket_type', 'new_status']
    search_fields = ['ticket_id', 'reassigned_by__username', 'notes']
    ordering = ['-reassigned_at']
