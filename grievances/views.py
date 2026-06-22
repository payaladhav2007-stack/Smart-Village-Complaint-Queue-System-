from django.shortcuts import render

def log_complaint(request):
    return render(request, 'grievances/log_complaint.html')

def map_picker(request):
    return render(request, 'grievances/map_picker.html')
