from django.urls import path
from .views import regional_dashboard, AnalyticsSummaryView

urlpatterns = [
    path('dashboard/', regional_dashboard, name='regional_dashboard'),
    path('summary/', AnalyticsSummaryView.as_view(), name='analytics_summary'),
]
