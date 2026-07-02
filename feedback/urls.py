from django.urls import path
from .views import feedback_form, SubmitFeedbackView

urlpatterns = [
    # Frontend page
    path('submit/', feedback_form, name='feedback_form'),

    # API endpoints
    path('api/submit/', SubmitFeedbackView.as_view(), name='submit_feedback_api'),
    path('submit/api/', SubmitFeedbackView.as_view(), name='submit_feedback_api2'),
]
