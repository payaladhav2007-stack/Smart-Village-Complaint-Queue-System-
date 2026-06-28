from django.urls import path
from .views import (
    log_complaint,
    map_picker,
    my_complaints,
    SubmitComplaintView,
    ListComplaintsView,
)

urlpatterns = [
    # Frontend pages
    path('log/', log_complaint, name='log_complaint'),
    path('map/', map_picker, name='map_picker'),
    path('my-complaints/', my_complaints, name='my_complaints'),

    # API endpoints
    path('submit/', SubmitComplaintView.as_view(), name='submit_complaint'),
    path('list/', ListComplaintsView.as_view(), name='list_complaints'),
]
