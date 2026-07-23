from django.urls import path
from accounts.views import DistrictListView, TalukaListView, VillageCityListView

urlpatterns = [
    path('districts/', DistrictListView.as_view(), name='location-districts'),
    path('talukas/', TalukaListView.as_view(), name='location-talukas'),
    path('villages/', VillageCityListView.as_view(), name='location-villages'),
]
