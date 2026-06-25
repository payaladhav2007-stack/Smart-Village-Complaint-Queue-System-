from django.shortcuts import render

def certificate_request(request):
    return render(request, 'appointments/certificate_request.html')

def queue_dashboard(request):
    return render(request, 'appointments/queue_dashboard.html')  
