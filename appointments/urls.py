from django.urls import path
from .views import (
    BookAppointmentView,
    ListMyAppointmentsView,
    certificate_request,
    queue_dashboard,
    time_slot_picker,
    token_confirmation,
)

urlpatterns = [
    # API endpoints
    path('book/', BookAppointmentView.as_view(), name='book_appointment'),
    path('my-tokens/', ListMyAppointmentsView.as_view(), name='my_tokens'),

    # Frontend pages
    path('request/', certificate_request, name='certificate_request'),
    path('queue/', queue_dashboard, name='queue_dashboard'),
    path('slots/', time_slot_picker, name='time_slot_picker'),
    path('confirmation/', token_confirmation, name='token_confirmation'),
]
