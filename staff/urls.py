from django.urls import path
from .views import workbench, grievance_management, token_tracking_console, control_panel, workload_charts, backlog_alerts

urlpatterns = [
    path('workbench/', workbench, name='workbench'),
    path('grievances/', grievance_management, name='grievance_management'),
    path('token-console/', token_tracking_console, name='token_tracking_console'),
    path('control-panel/', control_panel, name='control_panel'),
    path('workload-charts/', workload_charts, name='workload_charts'),
    path('backlog-alerts/', backlog_alerts, name='backlog_alerts'),
]