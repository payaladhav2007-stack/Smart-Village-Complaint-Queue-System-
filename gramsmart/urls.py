from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static

def health_check(request):
    return JsonResponse({"status": "GramSmart server is running"})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', health_check),
    path('sms/', include('sms_auth.urls')),
    path('api/auth/', include('accounts.urls')),  # GS-105/106 routing
    path('api/grievances/', include('grievances.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)