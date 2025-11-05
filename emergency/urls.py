from django.urls import path
from .views import *
urlpatterns=[
  path('emergency_req/',EmergencyRequestView.as_view(),name="emergency_req"),
  path('ping_location/',VolunteerLocationView.as_view(),name="ping_location"),
  path('emergency_accept/',RespondView.as_view(),name='emergency_accept'),
]