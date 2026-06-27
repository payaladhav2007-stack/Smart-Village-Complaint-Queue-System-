from django.urls import path
from .views import WorkbenchSummaryView

urlpatterns = [
    path('summary/', WorkbenchSummaryView.as_view(), name='workbench-summary'),
]
