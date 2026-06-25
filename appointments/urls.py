from django.urls import path
from .views import certificate_request, queue_dashboard

urlpatterns = [
    path('request/', certificate_request, name='certificate_request'),
    path('queue/', queue_dashboard, name='queue_dashboard'),
]
