from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Complaint
from .serializers import ComplaintSerializer


class SubmitComplaintView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        serializer = ComplaintSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListComplaintsView(ListAPIView):
    serializer_class = ComplaintSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        role = getattr(user, 'role', 'citizen')

        if role in ['sarpanch', 'staff']:
            queryset = Complaint.objects.all()
        else:
            queryset = Complaint.objects.filter(user=user)

        main_category = self.request.query_params.get('main_category')
        sub_category = self.request.query_params.get('sub_category')
        status_param = self.request.query_params.get('status')

        if main_category:
            queryset = queryset.filter(main_category=main_category)
        if sub_category:
            queryset = queryset.filter(sub_category=sub_category)
        if status_param:
            queryset = queryset.filter(status=status_param)

        return queryset


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
