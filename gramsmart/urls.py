from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

# Health check view to verify routing is working
def health_check(request):
    return JsonResponse({
        'status': 'ok',
        'message': 'GramSmart server is running'
    })

urlpatterns = [
    # Admin panel route
    path('admin/', admin.site.urls),

    # Health check route
    path('', health_check, name='health-check'),

    # Future module routes will be added here
    # path('api/grievances/', include('grievances.urls')),
    # path('api/appointments/', include('appointments.urls')),
]
