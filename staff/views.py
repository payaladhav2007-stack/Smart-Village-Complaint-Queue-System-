from django.shortcuts import render

def workbench(request):
    return render(request, 'staff/workbench.html')

def grievance_management(request):
    return render(request, 'staff/grievance_management.html')
