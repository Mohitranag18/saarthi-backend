from rest_framework import serializers
from .models import AccessibilityReport, RouteFeedback
from django.contrib.auth.models import User
from django.conf import settings
from .storage import supabase_storage
import os


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
    photo = serializers.ImageField(required=False, write_only=True)
    
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
            'photo',
        ]
        extra_kwargs = {
            'photo_url': {'required': False, 'allow_null': True}
        }

    def validate_photo(self, value):
        """Validate uploaded photo."""
        if value:
            # Check file size
            if value.size > getattr(settings, 'MAX_UPLOAD_SIZE', 10 * 1024 * 1024):
                raise serializers.ValidationError(
                    f"File size cannot exceed {getattr(settings, 'MAX_UPLOAD_SIZE', 10 * 1024 * 1024) // (1024 * 1024)}MB"
                )
            
            # Check file extension
            file_extension = os.path.splitext(value.name)[1].lower()
            allowed_extensions = getattr(settings, 'ALLOWED_UPLOAD_EXTENSIONS', ['.jpg', '.jpeg', '.png', '.gif', '.webp'])
            
            if file_extension not in allowed_extensions:
                raise serializers.ValidationError(
                    f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
                )
        
        return value

    def create(self, validated_data):
        """Create report with optional photo upload to Supabase."""
        photo = validated_data.pop('photo', None)
        
        # Handle user assignment (get or create default user)
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['user'] = request.user
        else:
            # Create or get a default user for testing
            from django.contrib.auth.models import User
            default_user, created = User.objects.get_or_create(
                username='testuser',
                defaults={'email': 'test@example.com'}
            )
            validated_data['user'] = default_user
        
        # Handle photo upload to Supabase
        if photo:
            if not supabase_storage.is_configured():
                # Log warning but allow creation without photo
                import logging
                logger = logging.getLogger(__name__)
                logger.warning("Supabase storage not configured, skipping photo upload")
            else:
                photo_url = supabase_storage.upload_file(photo)
                if photo_url:
                    validated_data['photo_url'] = photo_url
                else:
                    # Log error but allow creation without photo
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error("Failed to upload photo to Supabase")
        
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
