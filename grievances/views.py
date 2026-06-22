from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Complaint


class SubmitComplaintView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser] 
def log_complaint(request):
    return render(request, 'grievances/log_complaint.html')


def map_picker(request):
    return render(request, 'grievances/map_picker.html')


    def get_queryset(self):
        user = self.request.user
        queryset = Complaint.objects.all() if user.role in ('admin', 'staff') else Complaint.objects.filter(user=user)
        category = self.request.query_params.get('category')
        status_param = self.request.query_params.get('status')
        if category:
            queryset = queryset.filter(category=category)
        if status_param:
            queryset = queryset.filter(status=status_param)
        return queryset
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
