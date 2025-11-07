from rest_framework import serializers
from .models import AccessibilityReport, RouteFeedback
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class AccessibilityReportSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = AccessibilityReport
        fields = [
            'id',
            'latitude',
            'longitude',
            'problem_type',
            'disability_types',
            'severity',
            'description',
            'photo_url',
            'status',
            'created_at',
            'updated_at',
            'user',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']

    def validate_description(self, value):
        if len(value) > 200:
            raise serializers.ValidationError("Description must be 200 characters or less.")
        return value

    def validate_disability_types(self, value):
        if not isinstance(value, list) or len(value) == 0:
            raise serializers.ValidationError("At least one disability type must be selected.")
        return value


class AccessibilityReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessibilityReport
        fields = [
            'latitude',
            'longitude',
            'problem_type',
            'disability_types',
            'severity',
            'description',
            'photo_url',
        ]

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class RouteFeedbackSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = RouteFeedback
        fields = [
            'id',
            'start_lat',
            'start_lon',
            'end_lat',
            'end_lon',
            'disability_type',
            'rating',
            'comment',
            'created_at',
            'user',
        ]
        read_only_fields = ['id', 'created_at', 'user']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class RouteCalculationSerializer(serializers.Serializer):
    start = serializers.DictField(child=serializers.FloatField())
    end = serializers.DictField(child=serializers.FloatField())
    user_disability = serializers.CharField(max_length=50)

    def validate_start(self, value):
        if 'lat' not in value or 'lon' not in value:
            raise serializers.ValidationError("Start location must include 'lat' and 'lon'.")
        return value

    def validate_end(self, value):
        if 'lat' not in value or 'lon' not in value:
            raise serializers.ValidationError("End location must include 'lat' and 'lon'.")
        return value