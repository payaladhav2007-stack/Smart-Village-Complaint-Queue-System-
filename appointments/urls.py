from django.urls import path
from .views import certificate_request

urlpatterns = [
    path('request/', certificate_request, name='certificate_request'),
]
