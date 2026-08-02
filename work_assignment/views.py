from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import WorkAssignment
from .serializers import (
    WorkAssignmentCreateSerializer,
    WorkAssignmentListSerializer,
    WorkAssignmentStatusUpdateSerializer,
)
from .permissions import IsSarpanch, IsStaff, IsSarpanchOrStaff

User = get_user_model()


class CreateAssignmentView(APIView):
    """
    GS-REG-109: Sarpanch creates a work assignment for approved Staff
    in their own village_city.
    POST /api/work/assign/
    """
    permission_classes = [IsAuthenticated, IsSarpanch]

    def post(self, request):
        serializer = WorkAssignmentCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            assignment = serializer.save()
            return Response({
                'success': True,
                'message': 'Task assigned successfully.',
                'assignment': WorkAssignmentListSerializer(assignment).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class SarpanchAssignmentListView(APIView):
    """
    GS-REG-109: Sarpanch views all assignments they have created.
    GET /api/work/my-assignments/
    """
    permission_classes = [IsAuthenticated, IsSarpanch]

    def get(self, request):
        assignments = WorkAssignment.objects.filter(
            assigned_by=request.user
        ).select_related('assigned_to', 'assigned_by', 'related_complaint')

        serializer = WorkAssignmentListSerializer(assignments, many=True)
        return Response({
            'count': assignments.count(),
            'assignments': serializer.data
        })


class StaffAssignmentListView(APIView):
    """
    GS-REG-109: Staff views all tasks assigned to them.
    GET /api/work/my-tasks/
    """
    permission_classes = [IsAuthenticated, IsStaff]

    def get(self, request):
        assignments = WorkAssignment.objects.filter(
            assigned_to=request.user
        ).select_related('assigned_by', 'related_complaint')

        serializer = WorkAssignmentListSerializer(assignments, many=True)
        return Response({
            'count': assignments.count(),
            'assignments': serializer.data
        })


class StaffUpdateAssignmentStatusView(APIView):
    """
    GS-REG-109: Staff updates status of a task assigned to them.
    PATCH /api/work/tasks/<id>/update-status/
    """
    permission_classes = [IsAuthenticated, IsStaff]

    def patch(self, request, pk):
        try:
            assignment = WorkAssignment.objects.get(pk=pk, assigned_to=request.user)
        except WorkAssignment.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Task not found or not assigned to you.'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = WorkAssignmentStatusUpdateSerializer(
            assignment, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': f'Task status updated to {assignment.status}.',
                'assignment': WorkAssignmentListSerializer(assignment).data
            })
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class ListApprovedStaffView(APIView):
    """
    GS-REG-109: Sarpanch lists all approved Staff in their village_city.
    GET /api/work/available-staff/
    """
    permission_classes = [IsAuthenticated, IsSarpanch]

    def get(self, request):
        staff_list = User.objects.filter(
            role='staff',
            approval_status='approved',
            village_city=request.user.village_city
        ).values('id', 'username', 'phone_number', 'ward_number')

        return Response({
            'village_city': str(request.user.village_city) if request.user.village_city else None,
            'staff_count': staff_list.count(),
            'staff': list(staff_list)
        })


# ============================================================
# Frontend Dashboard Views
# ============================================================

@login_required
def sarpanch_dashboard(request):
    """Sarpanch dashboard — assign tasks and view all assignments."""
    if request.user.role != 'sarpanch' or request.user.approval_status != 'approved':
        return render(request, 'work_assignment/access_denied.html')

    staff_list = User.objects.filter(
        role='staff',
        approval_status='approved',
        village_city=request.user.village_city
    )
    assignments = WorkAssignment.objects.filter(
        assigned_by=request.user
    ).select_related('assigned_to')

    context = {
        'staff_list': staff_list,
        'assignments': assignments,
        'user': request.user,
        'pending_count': assignments.filter(status='pending').count(),
        'in_progress_count': assignments.filter(status='in_progress').count(),
        'completed_count': assignments.filter(status='completed').count(),
    }
    return render(request, 'work_assignment/sarpanch_dashboard.html', context)


@login_required
def staff_dashboard(request):
    """Staff dashboard — view and update assigned tasks."""
    if request.user.role != 'staff' or request.user.approval_status != 'approved':
        return render(request, 'work_assignment/access_denied.html')

    assignments = WorkAssignment.objects.filter(
        assigned_to=request.user
    ).select_related('assigned_by')

    context = {
        'assignments': assignments,
        'user': request.user,
        'pending_count': assignments.filter(status='pending').count(),
        'in_progress_count': assignments.filter(status='in_progress').count(),
        'completed_count': assignments.filter(status='completed').count(),
    }
    return render(request, 'work_assignment/staff_dashboard.html', context)

from django.shortcuts import redirect
from django.views.decorators.http import require_POST

@login_required
@require_POST
def update_task_status_form(request, pk):
    """Handles HTML form POST to update task status from staff dashboard."""
    if request.user.role != 'staff' or request.user.approval_status != 'approved':
        return render(request, 'work_assignment/access_denied.html')
    try:
        assignment = WorkAssignment.objects.get(pk=pk, assigned_to=request.user)
        new_status = request.POST.get('status')
        if new_status in ['pending', 'in_progress', 'completed']:
            assignment.status = new_status
            assignment.save()
    except WorkAssignment.DoesNotExist:
        pass
    return redirect('/work/dashboard/staff/')