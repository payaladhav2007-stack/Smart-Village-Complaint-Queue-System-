from django.urls import path
from .views import regional_dashboard

urlpatterns = [
    path('dashboard/', regional_dashboard, name='regional_dashboard'),
]
