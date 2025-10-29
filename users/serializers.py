from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
import uuid

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone_number', 'user_type',
            'disability_type', 'needs_wheelchair_access',
            'needs_tactile_paths', 'needs_audio_guidance'
        ]
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        
        # Generate QR code for volunteers
        if validated_data.get('user_type') == 'volunteer':
            validated_data['volunteer_qr_code'] = f"VOL-{uuid.uuid4().hex[:8].upper()}"
        
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile
    """
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone_number', 'user_type', 'disability_type',
            'needs_wheelchair_access', 'needs_tactile_paths',
            'needs_audio_guidance', 'is_volunteer_active',
            'volunteer_rating', 'volunteer_points', 'volunteer_qr_code',
            'profile_picture', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'volunteer_rating', 'volunteer_points']


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile
    """
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone_number',
            'disability_type', 'needs_wheelchair_access',
            'needs_tactile_paths', 'needs_audio_guidance',
            'profile_picture'
        ]