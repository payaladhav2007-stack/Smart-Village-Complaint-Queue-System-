from django.urls import path
from .views import certificate_request, queue_dashboard, time_slot_picker, token_confirmation

urlpatterns = [
    path('request/', certificate_request, name='certificate_request'),
    path('queue/', queue_dashboard, name='queue_dashboard'),
    path('slots/', time_slot_picker, name='time_slot_picker'),
    path('confirmation/', token_confirmation, name='token_confirmation'),
]