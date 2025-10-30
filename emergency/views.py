from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny

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
