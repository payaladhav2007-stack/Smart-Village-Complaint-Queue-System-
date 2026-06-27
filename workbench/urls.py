from django.urls import path
from .views import WorkbenchSummaryView, ReassignView

urlpatterns = [
    path('summary/', WorkbenchSummaryView.as_view(), name='workbench-summary'),
    path('reassign/', ReassignView.as_view(), name='workbench-reassign'),
]
