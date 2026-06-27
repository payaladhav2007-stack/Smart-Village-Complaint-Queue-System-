from django.urls import path
from .views import WorkbenchSummaryView, ReassignView, TicketTransitionView

urlpatterns = [
    path('summary/', WorkbenchSummaryView.as_view(), name='workbench-summary'),
    path('reassign/', ReassignView.as_view(), name='workbench-reassign'),
    path('transition/', TicketTransitionView.as_view(), name='ticket-transition'),
]