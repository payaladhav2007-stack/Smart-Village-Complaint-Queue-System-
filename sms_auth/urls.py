from django.urls import path
from . import views

urlpatterns = [
    path('verify/', views.sms_auth_endpoint, name='sms_auth_verify'),
]