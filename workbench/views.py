from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from grievances.models import Complaint
from appointments.models import Appointment
from .permissions import IsStaffOrAdmin


class WorkbenchSummaryView(APIView):
    permission_classes = [IsStaffOrAdmin]

    def get(self, request):

        # --- Pending Infrastructure Complaints ---
        pending_complaints = Complaint.objects.filter(
            status='pending'
        ).select_related('user').order_by('-created_at')

        complaints_data = [
            {
                'id': c.id,
                'category': c.category,
                'description': c.description[:100],
                'status': c.status,
                'latitude': str(c.latitude) if c.latitude else None,
                'longitude': str(c.longitude) if c.longitude else None,
                'submitted_by': c.user.username,
                'ward_number': c.user.ward_number,
                'created_at': c.created_at.isoformat(),
            }
            for c in pending_complaints
        ]

        # --- Upcoming Daily Token Slots ---
        today_start = timezone.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        today_end = timezone.now().replace(
            hour=23, minute=59, second=59, microsecond=999999
        )

        upcoming_appointments = Appointment.objects.filter(
            scheduled_time__gte=today_start,
            scheduled_time__lte=today_end,
            status__in=['pending', 'confirmed']
        ).select_related('user').order_by('scheduled_time')

        appointments_data = [
            {
                'id': a.id,
                'token_number': a.token_number,
                'service_type': a.service_type,
                'scheduled_time': a.scheduled_time.isoformat(),
                'status': a.status,
                'citizen': a.user.username,
                'ward_number': a.user.ward_number,
                'form_data_jsonb': a.form_data_jsonb,
            }
            for a in upcoming_appointments
        ]

        # --- Summary Metrics ---
        total_pending_complaints = Complaint.objects.filter(
            status='pending'
        ).count()

        total_in_progress_complaints = Complaint.objects.filter(
            status='in_progress'
        ).count()

        total_todays_appointments = upcoming_appointments.count()

        return Response({
            'workbench_summary': {
                'metrics': {
                    'pending_complaints': total_pending_complaints,
                    'in_progress_complaints': total_in_progress_complaints,
                    'todays_appointments': total_todays_appointments,
                },
                'pending_infrastructure_complaints': complaints_data,
                'upcoming_token_slots': appointments_data,
            }
        }, status=status.HTTP_200_OK)
