from rest_framework import serializers
from .models import AccessibilityReport, RouteFeedback
from django.contrib.auth import get_user_model
from django.conf import settings
from .storage import supabase_storage
import os

User = get_user_model()


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
        # Handle both list and string (from FormData)
        print(f"🔍 Validating disability_types: {value} (Type: {type(value).__name__})")
        
        if isinstance(value, str):
            # Convert comma-separated string to list
            disability_types = [type.strip() for type in value.split(',') if type.strip()]
            print(f"🔄 Converted string to list: {disability_types}")
            if not disability_types:
                raise serializers.ValidationError("At least one disability type must be selected.")
            return disability_types
        elif isinstance(value, list):
            print(f"📝 Received list directly: {value}")
            if len(value) == 0:
                raise serializers.ValidationError("At least one disability type must be selected.")
            return value
        else:
            print(f"❌ Invalid type for disability_types: {type(value)}")
            raise serializers.ValidationError("Invalid format for disability types.")


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

    def validate_disability_types(self, value):
        # Handle both list and string (from FormData)
        if isinstance(value, str):
            # Convert comma-separated string to list
            disability_types = [type.strip() for type in value.split(',') if type.strip()]
            if not disability_types:
                raise serializers.ValidationError("At least one disability type must be selected.")
            return disability_types
        elif isinstance(value, list):
            if len(value) == 0:
                raise serializers.ValidationError("At least one disability type must be selected.")
            return value
        else:
            raise serializers.ValidationError("Invalid format for disability types.")

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
            from django.contrib.auth import get_user_model
            User = get_user_model()
            default_user, created = User.objects.get_or_create(
                username='testuser',
                defaults={'email': 'test@example.com'}
            )
            validated_data['user'] = default_user
        
        # Handle photo upload to Supabase
        if photo:
            import logging
            logger = logging.getLogger(__name__)
            
            logger.info(f"Processing photo upload: {photo.name}")
            
            if not supabase_storage.is_configured():
                # Log warning but allow creation without photo
                logger.warning("Supabase storage not configured, skipping photo upload")
            else:
                try:
                    logger.info("Starting Supabase upload...")
                    photo_url = supabase_storage.upload_file(photo)
                    if photo_url:
                        validated_data['photo_url'] = photo_url
                        logger.info(f"Photo uploaded successfully: {photo_url}")
                    else:
                        # Log error but allow creation without photo
                        logger.error("Failed to upload photo to Supabase - no URL returned")
                except Exception as e:
                    # Log error but allow creation without photo
                    logger.error(f"Exception during photo upload to Supabase: {e}")
                    logger.exception("Full exception details:")
        
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
