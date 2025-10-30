from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import EmergencyRequests,VolunteerLocations

class EmergencyRequestSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = EmergencyRequests
        geo_field = "location"   # tell it which field is the geometry
        fields = [
            'id',
            'location',
            'description',
            'status',
            'qr_verified',
            'created_at',
            'completed_at',
            'volunteer',
            'user',
        ]
        read_only_fields = [
            'id',
            'user',
            'status',
            'qr_verified',
            'created_at',
            'completed_at'
        ]

    def create(self, validated_data):
        # Automatically set the user to the currently authenticated user
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)

class VolunteerLocationSerializer(GeoFeatureModelSerializer):
    class Meta:
        model=VolunteerLocations
        geo_field="location"
        fields = ['id', 'user', 'location', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
    def create(self, validated_data):
        # Automatically set the user to the currently authenticated user
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)