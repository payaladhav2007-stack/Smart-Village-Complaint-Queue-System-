from django.shortcuts import render

def regional_dashboard(request):
    return render(request, 'analytics/regional_dashboard.html')
