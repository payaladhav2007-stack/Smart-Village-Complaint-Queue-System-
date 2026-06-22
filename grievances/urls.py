from django.urls import path
from .views import SubmitComplaintView, ListComplaintsView

urlpatterns = [
    path('submit/', SubmitComplaintView.as_view(), name='submit-complaint'),
    path('list/', ListComplaintsView.as_view(), name='list-complaints'),
]