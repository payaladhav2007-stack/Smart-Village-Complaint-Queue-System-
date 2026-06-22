from django.urls import path
from .views import SubmitComplaintView

urlpatterns = [
    path('submit/', SubmitComplaintView.as_view(), name='submit-complaint'),
]

