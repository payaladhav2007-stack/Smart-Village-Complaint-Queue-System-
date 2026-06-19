from django.urls import path
from . import views

urlpatterns = [
    path('request-otp/', views.request_otp, name='sms_request_otp'),
    path('verify/', views.verify_otp, name='sms_auth_verify'),
]