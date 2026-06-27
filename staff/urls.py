from django.urls import path
from .views import workbench

urlpatterns = [
    path('workbench/', workbench, name='workbench'),
]
