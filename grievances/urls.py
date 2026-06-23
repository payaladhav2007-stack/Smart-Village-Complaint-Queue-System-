from django.urls import path
from .views import log_complaint, map_picker, my_complaints

urlpatterns = [
    path('log/', log_complaint, name='log_complaint'),
    path('map/', map_picker, name='map_picker'),
    path('my-complaints/', my_complaints, name='my_complaints'),
]
