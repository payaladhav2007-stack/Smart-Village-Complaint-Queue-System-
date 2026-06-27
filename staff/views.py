from django.shortcuts import render

def workbench(request):
    return render(request, 'staff/workbench.html')
