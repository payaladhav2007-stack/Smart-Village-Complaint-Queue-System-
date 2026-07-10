from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg, Count, F, ExpressionWrapper, DurationField
from django.utils import timezone
from datetime import timedelta
from grievances.models import Complaint
from appointments.models import Appointment
from workbench.permissions import IsStaffOrAdmin


class AnalyticsSummaryView(APIView):
    permission_classes = [IsAuthenticated, IsStaffOrAdmin]

    def get(self, request):
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)

        total_complaints = Complaint.objects.count()
        resolved_complaints = Complaint.objects.filter(status='resolved').count()
        pending_complaints = Complaint.objects.filter(status='pending').count()
        in_progress_complaints = Complaint.objects.filter(status='in_progress').count()
        rejected_complaints = Complaint.objects.filter(status='rejected').count()

        resolved_with_time = Complaint.objects.filter(
            status='resolved'
        ).annotate(
            resolution_time=ExpressionWrapper(
                F('updated_at') - F('created_at'),
                output_field=DurationField()
            )
        ).aggregate(avg_resolution=Avg('resolution_time'))

        avg_resolution_hours = None
        if resolved_with_time['avg_resolution']:
            avg_resolution_hours = round(
                resolved_with_time['avg_resolution'].total_seconds() / 3600, 2
            )

        backlog_by_category = list(
            Complaint.objects.filter(
                status__in=['pending', 'in_progress']
            ).values('category').annotate(
                count=Count('id')
            ).order_by('-count')
        )

        recent_complaints = Complaint.objects.filter(
            created_at__gte=thirty_days_ago
        ).count()

        resolution_rate = None
        if total_complaints > 0:
            resolution_rate = round((resolved_complaints / total_complaints) * 100, 2)

        total_appointments = Appointment.objects.count()
        pending_appointments = Appointment.objects.filter(status='pending').count()
        confirmed_appointments = Appointment.objects.filter(status='confirmed').count()
        completed_appointments = Appointment.objects.filter(status='completed').count()
        cancelled_appointments = Appointment.objects.filter(status='cancelled').count()

        appointments_by_service = list(
            Appointment.objects.values('service_type').annotate(
                count=Count('id')
            ).order_by('-count')
        )

        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        todays_appointments = Appointment.objects.filter(
            scheduled_time__range=(today_start, today_end)
        ).count()

        # GS-ADV-107: Main category breakdown
        main_category_breakdown = list(
            Complaint.objects.values('main_category').annotate(
                count=Count('id')
            ).order_by('-count')
        )

        # GS-ADV-107: Sub category breakdown
        sub_category_breakdown = list(
            Complaint.objects.exclude(
                sub_category=''
            ).values('main_category', 'sub_category').annotate(
                count=Count('id')
            ).order_by('main_category', '-count')
        )

        return Response({
            "analytics_summary": {
                "generated_at": now.isoformat(),
                "grievance_kpis": {
                    "total_complaints": total_complaints,
                    "resolved": resolved_complaints,
                    "pending": pending_complaints,
                    "in_progress": in_progress_complaints,
                    "rejected": rejected_complaints,
                    "resolution_rate_percent": resolution_rate,
                    "avg_resolution_time_hours": avg_resolution_hours,
                    "recent_complaints_last_30_days": recent_complaints,
                    "unresolved_backlog_by_category": backlog_by_category,
                    "main_category_breakdown": main_category_breakdown,
                    "sub_category_breakdown": sub_category_breakdown,
                },
                "appointment_kpis": {
                    "total_appointments": total_appointments,
                    "pending": pending_appointments,
                    "confirmed": confirmed_appointments,
                    "completed": completed_appointments,
                    "cancelled": cancelled_appointments,
                    "todays_appointments": todays_appointments,
                    "appointments_by_service_type": appointments_by_service,
                }
            }
        })


def regional_dashboard(request):
    return render(request, 'analytics/regional_dashboard.html')
