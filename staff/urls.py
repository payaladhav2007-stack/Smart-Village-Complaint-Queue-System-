from django.urls import path
from .views import workbench, grievance_management, token_tracking_console

urlpatterns = [
    path('workbench/', workbench, name='workbench'),
    path('grievances/', grievance_management, name='grievance_management'),
    path('token-console/', token_tracking_console, name='token_tracking_console'),
]