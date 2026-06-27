from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from grievances.models import Complaint
from appointments.models import Appointment
from .permissions import IsStaffOrAdmin
from django.db import transaction
from grievances.models import Complaint
from appointments.models import Appointment
from .models import ReassignmentLog
from .permissions import IsStaffOrAdmin
from .state_machine import is_valid_transition

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

class ReassignView(APIView):
    permission_classes = [IsStaffOrAdmin]

    def post(self, request):
        ticket_type = request.data.get('ticket_type')
        ticket_id = request.data.get('ticket_id')
        new_status = request.data.get('new_status')
        notes = request.data.get('notes', '')

        # Validate required fields
        if not ticket_type or not ticket_id or not new_status:
            return Response({
                'error': 'ticket_type, ticket_id and new_status are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate ticket type
        if ticket_type not in ['complaint', 'appointment']:
            return Response({
                'error': 'ticket_type must be either complaint or appointment.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                if ticket_type == 'complaint':
                    valid_statuses = ['pending', 'in_progress', 'resolved', 'rejected']
                    if new_status not in valid_statuses:
                        return Response({
                            'error': f'Invalid status for complaint. Must be one of: {", ".join(valid_statuses)}'
                        }, status=status.HTTP_400_BAD_REQUEST)

                    ticket = Complaint.objects.select_for_update().get(id=ticket_id)
                    previous_status = ticket.status
                    ticket.status = new_status
                    ticket.save()

                elif ticket_type == 'appointment':
                    valid_statuses = ['pending', 'confirmed', 'completed', 'cancelled']
                    if new_status not in valid_statuses:
                        return Response({
                            'error': f'Invalid status for appointment. Must be one of: {", ".join(valid_statuses)}'
                        }, status=status.HTTP_400_BAD_REQUEST)

                    ticket = Appointment.objects.select_for_update().get(id=ticket_id)
                    previous_status = ticket.status
                    ticket.status = new_status
                    ticket.save()

                # Record reassignment history
                log = ReassignmentLog.objects.create(
                    ticket_type=ticket_type,
                    ticket_id=ticket_id,
                    previous_status=previous_status,
                    new_status=new_status,
                    reassigned_by=request.user,
                    notes=notes
                )

                return Response({
                    'message': f'{ticket_type.capitalize()} #{ticket_id} successfully reassigned.',
                    'reassignment': {
                        'log_id': log.id,
                        'ticket_type': ticket_type,
                        'ticket_id': ticket_id,
                        'previous_status': previous_status,
                        'new_status': new_status,
                        'reassigned_by': request.user.username,
                        'notes': notes,
                        'reassigned_at': log.reassigned_at.isoformat()
                    }
                }, status=status.HTTP_200_OK)

        except Complaint.DoesNotExist:
            return Response({
                'error': f'Complaint #{ticket_id} not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        except Appointment.DoesNotExist:
            return Response({
                'error': f'Appointment #{ticket_id} not found.'
            }, status=status.HTTP_404_NOT_FOUND)
class TicketTransitionView(APIView):
    permission_classes = [IsStaffOrAdmin]

    def post(self, request):
        ticket_id = request.data.get('ticket_id')
        ticket_type = request.data.get('type')
        new_status = request.data.get('new_status')

        if not ticket_id or not ticket_type or not new_status:
            return Response({
                'error': 'ticket_id, type, and new_status are all required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if ticket_type not in ('grievance', 'appointment'):
            return Response({
                'error': "type must be 'grievance' or 'appointment'."
            }, status=status.HTTP_400_BAD_REQUEST)

        model = Complaint if ticket_type == 'grievance' else Appointment

        with transaction.atomic():
            try:
                ticket = model.objects.select_for_update().get(id=ticket_id)
            except model.DoesNotExist:
                return Response({
                    'error': f'No {ticket_type} found with id {ticket_id}.'
                }, status=status.HTTP_404_NOT_FOUND)

            current_status = ticket.status
            valid, error_message = is_valid_transition(ticket_type, current_status, new_status)

            if not valid:
                return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)

            ticket.status = new_status
            ticket.save()

            return Response({
                'message': f'{ticket_type.capitalize()} #{ticket_id} transitioned successfully.',
                'ticket_id': ticket.id,
                'type': ticket_type,
                'previous_status': current_status,
                'new_status': ticket.status,
            }, status=status.HTTP_200_OK)