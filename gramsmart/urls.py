from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({"status": "GramSmart server is running"})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', health_check),
    path('sms/', include('sms_auth.urls')),
    path('api/auth/', include('accounts.urls')),  # GS-105/106 routing
]