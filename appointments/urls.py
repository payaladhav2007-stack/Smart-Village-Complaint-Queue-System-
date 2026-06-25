from django.urls import path
from .views import BookAppointmentView, ListMyAppointmentsView

urlpatterns = [
    path('book/', BookAppointmentView.as_view(), name='book-appointment'),
    path('my-tokens/', ListMyAppointmentsView.as_view(), name='my-tokens'),
]