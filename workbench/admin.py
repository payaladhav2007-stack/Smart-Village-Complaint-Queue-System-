from django.contrib import admin
from .models import ReassignmentLog, NotificationLog


@admin.register(ReassignmentLog)
class ReassignmentLogAdmin(admin.ModelAdmin):
    list_display = ['ticket_type', 'ticket_id', 'previous_status', 'new_status', 'reassigned_by', 'reassigned_at']
    list_filter = ['ticket_type', 'new_status']
    search_fields = ['ticket_id', 'reassigned_by__username', 'notes']
    ordering = ['-reassigned_at']


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ['ticket_type', 'ticket_id', 'recipient_user', 'status_at_dispatch', 'dispatched_at']
    list_filter = ['ticket_type', 'status_at_dispatch']
    search_fields = ['ticket_id', 'recipient_user__username', 'message']
    ordering = ['-dispatched_at']