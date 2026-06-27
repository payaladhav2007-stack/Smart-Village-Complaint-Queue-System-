from django.shortcuts import render

def workbench(request):
    return render(request, 'staff/workbench.html')

def grievance_management(request):
    return render(request, 'staff/grievance_management.html')

def token_tracking_console(request):
    return render(request, 'staff/token_tracking_console.html')