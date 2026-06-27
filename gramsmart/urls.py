from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({"status": "GramSmart server is running"})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', health_check),
    path('api/auth/', include('accounts.urls')),
    path('grievances/', include('grievances.urls')),
    path('appointments/', include('appointments.urls')),
    path('api/appointments/', include('appointments.urls')),
    path('api/admin/workbench/', include('workbench.urls')),
]
