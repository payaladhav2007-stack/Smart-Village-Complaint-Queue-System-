from django.urls import path
from .views import workbench, grievance_management

urlpatterns = [
    path('workbench/', workbench, name='workbench'),
    path('grievances/', grievance_management, name='grievance_management'),
]
