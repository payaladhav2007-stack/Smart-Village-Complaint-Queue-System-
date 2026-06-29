from django.urls import path
from .views import SubmitFeedbackView

urlpatterns = [
    path('submit/', SubmitFeedbackView.as_view(), name='submit-feedback'),
]