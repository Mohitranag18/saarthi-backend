from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.views import APIView

from .models import EmergencyRequests, VolunteerLocations
from .serializers import EmergencyRequestSerializer,VolunteerLocationSerializer

from users.models import User


class EmergencyRequestView(generics.CreateAPIView):
    queryset = EmergencyRequests.objects.all()
    serializer_class = EmergencyRequestSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dummy_user = User.objects.first()
        emergency_request = serializer.save(user=dummy_user)

        # Get nearby volunteers (within 5 km)
        emergency_point = emergency_request.location
        nearby_volunteers = (
            VolunteerLocations.objects
            .filter(location__distance_lte=(emergency_point, D(km=5)))
            .annotate(distance=Distance('location', emergency_point))
            .order_by('distance')
        )

        # Convert volunteers to simple list
        volunteers_data = [
            {
                "id": v.user.id,
                "username": v.user.username,
                "distance_km": round(v.distance.km, 2),
                "lat": v.location.y,
                "lng": v.location.x
            }
            for v in nearby_volunteers
        ]

        # Return both created emergency and nearby list
        return Response(
            {
                "emergency": EmergencyRequestSerializer(emergency_request).data,
                "nearby_volunteers": volunteers_data,
            },
            status=status.HTTP_201_CREATED
        )
    

class VolunteerLocationView(generics.CreateAPIView):
    queryset= VolunteerLocations.objects.all()
    serializer_class = VolunteerLocationSerializer
    permission_classes = [AllowAny]    




class RespondView(APIView):
    permission_classes = [AllowAny]    
    def post(self, request):
        request_id = request.data.get("request_id")

        # validate input
        if not request_id:
            return Response({"error": "Missing request_id"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            emergency = EmergencyRequests.objects.get(id=request_id)
        except EmergencyRequests.DoesNotExist:
            return Response({"error": "Request not found"}, status=status.HTTP_404_NOT_FOUND)
        try:
            emergency.volunteer=User.objects.get(id=request.data.get("id"))
        except User.DoesNotExist:
            return Response({"error: kaun hai be?"},status=status.HTTP_400_BAD_REQUEST)
        emergency.save()
        location = emergency.location  # GeoDjango Point object

        # convert Point to lat/lng
        response_data = {
            "status": "success",
            "location": {
                "latitude": location.y,
                "longitude": location.x
            }
        }

        return Response(response_data, status=status.HTTP_200_OK)

