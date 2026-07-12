from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static
from workbench.views import TicketTransitionView
from feedback.views import SubmitFeedbackView

def health_check(request):
    return JsonResponse({"status": "GramSmart server is running"})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', health_check),
    path('i18n/', include('django.conf.urls.i18n')),
    path('api/auth/', include('accounts.urls')),
    path('grievances/', include('grievances.urls')),
    path('api/grievances/', include('grievances.urls')),
    path('appointments/', include('appointments.urls')),
    path('api/appointments/', include('appointments.urls')),
    path('api/admin/workbench/', include('workbench.urls')),
    path('api/admin/tickets/transition/', TicketTransitionView.as_view(), name='ticket-transition-exact'),
    path('staff/', include('staff.urls')),
    path('api/analytics/', include('analytics.urls')),
    path('api/feedback/submit/', SubmitFeedbackView.as_view(), name='feedback_submit_direct'),
    path('feedback/', include('feedback.urls')),
    path('api/feedback/', include('feedback.urls')),
    path('analytics/', include('analytics.urls')),] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
