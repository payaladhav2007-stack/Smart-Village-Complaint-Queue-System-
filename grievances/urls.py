from django.urls import path
from .views import log_complaint

urlpatterns = [
    path('log/', log_complaint, name='log_complaint'),
]
