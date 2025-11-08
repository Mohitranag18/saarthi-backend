#!/usr/bin/env python
"""
Test script to verify report creation functionality.
"""

import os
import sys
import django
from io import BytesIO
from PIL import Image

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saarthi_backend.settings')
django.setup()

from accessibility.serializers import AccessibilityReportCreateSerializer
from django.contrib.auth.models import User
from django.test import RequestFactory
from accessibility.storage import supabase_storage


def create_test_image():
    """Create a simple test image."""
    img = Image.new('RGB', (100, 100), color='blue')
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    from django.core.files.uploadedfile import SimpleUploadedFile
    return SimpleUploadedFile(
        "test_image.jpg",
        img_bytes.getvalue(),
        content_type="image/jpeg"
    )


def test_report_creation_without_photo():
    """Test creating a report without photo."""
    print("Testing report creation WITHOUT photo...")
    
    # Create test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )
    
    # Mock request
    factory = RequestFactory()
    request = factory.post('/')
    request.user = user
    
    # Test data
    data = {
        'latitude': 28.6139,
        'longitude': 77.2090,
        'problem_type': 'Broken Ramp',
        'disability_types': ['Wheelchair', 'Mobility Issues'],
        'severity': 'High',
        'description': 'Test report without photo'
    }
    
    # Test serializer
    serializer = AccessibilityReportCreateSerializer(
        data=data,
        context={'request': request}
    )
    
    if serializer.is_valid():
        report = serializer.save()
        print(f"✅ Report created successfully: {report.id}")
        print(f"   Photo URL: {report.photo_url}")
        return True
    else:
        print(f"❌ Validation failed: {serializer.errors}")
        return False


def test_report_creation_with_photo():
    """Test creating a report with photo."""
    print("\nTesting report creation WITH photo...")
    
    # Create test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )
    
    # Mock request
    factory = RequestFactory()
    request = factory.post('/')
    request.user = user
    
    # Test data
    test_photo = create_test_image()
    data = {
        'latitude': 28.6139,
        'longitude': 77.2090,
        'problem_type': 'Pothole',
        'disability_types': ['Wheelchair'],
        'severity': 'Critical',
        'description': 'Test report with photo',
        'photo': test_photo
    }
    
    # Test serializer
    serializer = AccessibilityReportCreateSerializer(
        data=data,
        context={'request': request}
    )
    
    if serializer.is_valid():
        report = serializer.save()
        print(f"✅ Report created successfully: {report.id}")
        print(f"   Photo URL: {report.photo_url}")
        return True
    else:
        print(f"❌ Validation failed: {serializer.errors}")
        return False


def test_supabase_status():
    """Test Supabase configuration status."""
    print("Checking Supabase configuration...")
    
    if supabase_storage.is_configured():
        print("✅ Supabase storage is configured")
    else:
        print("⚠️  Supabase storage is NOT configured")
        print("   Photos will not be uploaded until configured")


def main():
    """Run all tests."""
    print("🧪 Testing Report Creation Functionality")
    print("=" * 50)
    
    # Check Supabase status
    test_supabase_status()
    
    # Test without photo
    success1 = test_report_creation_without_photo()
    
    # Test with photo
    success2 = test_report_creation_with_photo()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"Report without photo: {'✅' if success1 else '❌'}")
    print(f"Report with photo: {'✅' if success2 else '❌'}")
    
    if success1 and success2:
        print("\n🎉 All tests passed! Report creation is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
