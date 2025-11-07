from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from math import radians, cos, sin, asin, sqrt
import requests
from django.conf import settings

from .models import AccessibilityReport, RouteFeedback
from .serializers import (
    AccessibilityReportSerializer,
    AccessibilityReportCreateSerializer,
    RouteFeedbackSerializer,
    RouteCalculationSerializer,
)


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in kilometers."""
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6371 * c
    return km


class AccessibilityReportListCreateView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get all reports, optionally filtered by location and radius."""
        lat = request.query_params.get('lat')
        lon = request.query_params.get('lon')
        radius = float(request.query_params.get('radius', 10))  # Default 10km
        severity = request.query_params.get('severity')
        status_filter = request.query_params.get('status', 'Active')

        reports = AccessibilityReport.objects.filter(status=status_filter)

        if severity:
            reports = reports.filter(severity=severity)

        # Filter by location if provided
        if lat and lon:
            lat = float(lat)
            lon = float(lon)
            filtered_reports = []
            
            for report in reports:
                distance = haversine_distance(
                    lat, lon,
                    float(report.latitude), float(report.longitude)
                )
                if distance <= radius:
                    filtered_reports.append(report)
            
            reports = filtered_reports

        serializer = AccessibilityReportSerializer(reports, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Create a new accessibility report."""
        serializer = AccessibilityReportCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            report = serializer.save()
            response_serializer = AccessibilityReportSerializer(report)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AccessibilityReportDetailView(APIView):
    # permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return AccessibilityReport.objects.get(pk=pk)
        except AccessibilityReport.DoesNotExist:
            return None

    def get(self, request, pk):
        """Get a specific report."""
        report = self.get_object(pk)
        if not report:
            return Response(
                {'error': 'Report not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = AccessibilityReportSerializer(report)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        """Update a report (owner only)."""
        report = self.get_object(pk)
        if not report:
            return Response(
                {'error': 'Report not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if report.user != request.user:
            return Response(
                {'error': 'You do not have permission to edit this report'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = AccessibilityReportSerializer(
            report,
            data=request.data,
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """Delete a report (owner only)."""
        report = self.get_object(pk)
        if not report:
            return Response(
                {'error': 'Report not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if report.user != request.user:
            return Response(
                {'error': 'You do not have permission to delete this report'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        report.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RouteCalculationView(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        """Calculate accessible routes between two points."""
        serializer = RouteCalculationSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        start = data['start']
        end = data['end']
        disability = data['user_disability']

        # Get weather data
        weather = self.get_weather(start['lat'], start['lon'])

        # Get nearby reports
        reports = self.get_nearby_reports(start, end, disability)

        # Calculate routes
        routes = self.calculate_routes(start, end, reports, weather, disability)

        return Response({
            'routes': routes,
            'weather': weather,
        }, status=status.HTTP_200_OK)

    def get_weather(self, lat, lon):
        """Get weather data from OpenWeatherMap."""
        api_key = getattr(settings, 'OPENWEATHER_API_KEY', None)
        if not api_key:
            return {'condition': 'Unknown', 'temperature': 20}

        try:
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': api_key,
                'units': 'metric'
            }
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'condition': data['weather'][0]['main'],
                    'temperature': round(data['main']['temp'])
                }
        except Exception as e:
            print(f"Weather API error: {e}")
        
        return {'condition': 'Unknown', 'temperature': 20}

    def get_nearby_reports(self, start, end, disability):
        """Get reports near the route."""
        # Calculate bounding box
        min_lat = min(start['lat'], end['lat']) - 0.1
        max_lat = max(start['lat'], end['lat']) + 0.1
        min_lon = min(start['lon'], end['lon']) - 0.1
        max_lon = max(start['lon'], end['lon']) + 0.1

        # Mapping disability profiles to disability types
        disability_mapping = {
            'wheelchair': 'Wheelchair',
            'visual': 'Visual Impairment',
            'hearing': 'Hearing Impairment',
            'mobility': 'Mobility Issues',
        }
        
        disability_type = disability_mapping.get(disability, 'Wheelchair')

        reports = AccessibilityReport.objects.filter(
            status='Active',
            latitude__gte=min_lat,
            latitude__lte=max_lat,
            longitude__gte=min_lon,
            longitude__lte=max_lon,
        )

        # Filter reports relevant to user's disability
        relevant_reports = []
        for report in reports:
            if disability_type in report.disability_types:
                relevant_reports.append(report)

        return relevant_reports

    def calculate_routes(self, start, end, reports, weather, disability):
        """Calculate three route options."""
        distance = haversine_distance(
            start['lat'], start['lon'],
            end['lat'], end['lon']
        )

        # Count hazards by severity
        critical_count = sum(1 for r in reports if r.severity == 'Critical')
        high_count = sum(1 for r in reports if r.severity == 'High')
        medium_count = sum(1 for r in reports if r.severity == 'Medium')

        # Calculate base scores
        base_score = 100
        
        # Route 1: Fastest (direct route, minimal consideration for accessibility)
        fastest_score = base_score - (distance * 2)
        fastest_score -= (critical_count * 5 + high_count * 3)
        fastest_score = max(0, min(100, fastest_score))

        # Route 2: Safest (maximum accessibility, avoids all hazards)
        safest_distance = distance * 1.3  # 30% longer to avoid hazards
        safest_score = base_score - (safest_distance * 1.5)
        safest_score -= (critical_count * 2 + high_count * 1)
        
        # Weather bonus for safest route
        if weather['condition'] == 'Rain':
            safest_score += 10
        
        safest_score = max(0, min(100, safest_score))
        hazards_avoided = critical_count + high_count + medium_count

        # Route 3: Community Verified (balanced approach)
        community_distance = distance * 1.15  # 15% longer
        community_score = base_score - (community_distance * 1.8)
        community_score -= (critical_count * 3 + high_count * 2)
        community_score = max(0, min(100, community_score))

        routes = [
            {
                'type': 'fastest',
                'distance': f"{distance:.1f} km",
                'duration': f"{int(distance * 12)} min",
                'accessibility_score': round(fastest_score),
                'coordinates': [
                    [start['lon'], start['lat']],
                    [end['lon'], end['lat']],
                ]
            },
            {
                'type': 'safest',
                'distance': f"{safest_distance:.1f} km",
                'duration': f"{int(safest_distance * 12)} min",
                'accessibility_score': round(safest_score),
                'hazards_avoided': hazards_avoided,
                'coordinates': [
                    [start['lon'], start['lat']],
                    [(start['lon'] + end['lon']) / 2, (start['lat'] + end['lat']) / 2],
                    [end['lon'], end['lat']],
                ]
            },
            {
                'type': 'community_verified',
                'distance': f"{community_distance:.1f} km",
                'duration': f"{int(community_distance * 12)} min",
                'accessibility_score': round(community_score),
                'coordinates': [
                    [start['lon'], start['lat']],
                    [end['lon'], end['lat']],
                ]
            },
        ]

        return routes


class RouteFeedbackView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Submit feedback for a route."""
        serializer = RouteFeedbackSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            feedback = serializer.save()
            return Response(
                RouteFeedbackSerializer(feedback).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WeatherView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get current weather for a location."""
        lat = request.query_params.get('lat')
        lon = request.query_params.get('lon')

        if not lat or not lon:
            return Response(
                {'error': 'Latitude and longitude are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        api_key = getattr(settings, 'OPENWEATHER_API_KEY', None)
        if not api_key:
            return Response(
                {'condition': 'Unknown', 'temperature': 20},
                status=status.HTTP_200_OK
            )

        try:
            url = "http://api.openweathermap.org/data/2.5/weather"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': api_key,
                'units': 'metric'
            }
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                weather_data = {
                    'condition': data['weather'][0]['main'],
                    'description': data['weather'][0]['description'],
                    'temperature': round(data['main']['temp']),
                    'feels_like': round(data['main']['feels_like']),
                    'humidity': data['main']['humidity'],
                }
                return Response(weather_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Weather API error: {e}")
        
        return Response(
            {'condition': 'Unknown', 'temperature': 20},
            status=status.HTTP_200_OK
        )