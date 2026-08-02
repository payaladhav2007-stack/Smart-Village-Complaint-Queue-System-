from django.urls import path
from .views import NoticeListCreateView, NoticeDetailView

urlpatterns = [
    path('', NoticeListCreateView.as_view(), name='notice_list_create'),
    path('<int:pk>/', NoticeDetailView.as_view(), name='notice_detail'),
]