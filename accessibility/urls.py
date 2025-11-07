from django.urls import path
from .views import (
    AccessibilityReportListCreateView,
    AccessibilityReportDetailView,
    RouteCalculationView,
    RouteFeedbackView,
    WeatherView,
)

urlpatterns = [
    # Reports
    path('reports/', AccessibilityReportListCreateView.as_view(), name='report-list-create'),
    path('reports/<uuid:pk>/', AccessibilityReportDetailView.as_view(), name='report-detail'),
    
    # Routes
    path('routes/calculate/', RouteCalculationView.as_view(), name='route-calculate'),
    path('routes/feedback/', RouteFeedbackView.as_view(), name='route-feedback'),
    
    # Weather
    path('weather/', WeatherView.as_view(), name='weather'),
]