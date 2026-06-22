from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Complaint


def log_complaint(request):
    return render(request, 'grievances/log_complaint.html')


def map_picker(request):
    return render(request, 'grievances/map_picker.html')


@login_required
def my_complaints(request):
    complaints = Complaint.objects.filter(user=request.user).order_by('-created_at')
    total = complaints.count()
    pending = complaints.filter(status='pending').count()
    in_progress = complaints.filter(status='in_progress').count()
    resolved = complaints.filter(status='resolved').count()
    rejected = complaints.filter(status='rejected').count()

    context = {
        'complaints': complaints,
        'total': total,
        'pending': pending,
        'in_progress': in_progress,
        'resolved': resolved,
        'rejected': rejected,
    }
    return render(request, 'grievances/my_complaints.html', context)
