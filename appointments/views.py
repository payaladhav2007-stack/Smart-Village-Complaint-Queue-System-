from django.shortcuts import render

def certificate_request(request):
    return render(request, 'appointments/certificate_request.html')

def queue_dashboard(request):
    return render(request, 'appointments/queue_dashboard.html')

def time_slot_picker(request):
    return render(request, 'appointments/time_slot_picker.html')