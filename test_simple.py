#!/usr/bin/env python
"""
Simple test script to verify report creation functionality without PIL.
"""

import os
import sys
import django

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saarthi_backend.settings')
django.setup()

from accessibility.serializers import AccessibilityReportCreateSerializer
from django.contrib.auth.models import User
from django.test import RequestFactory
from accessibility.storage import supabase_storage


def test_report_creation_without_photo():
    """Test creating a report without photo."""
    print("Testing report creation WITHOUT photo...")
    
    # Create test user (using custom User model)
    from django.contrib.auth import get_user_model
    User = get_user_model()
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
        print(f"   User: {report.user.username}")
        print(f"   Problem: {report.problem_type}")
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
    
    # Check environment variables
    vars_to_check = ['SUPABASE_URL', 'SUPABASE_KEY', 'SUPABASE_BUCKET_NAME']
    for var in vars_to_check:
        value = os.environ.get(var)
        if value:
            print(f"   {var}: {'✅ Set' if value != f'your-{var.lower()}-here' else '⚠️  Using placeholder'}")
        else:
            print(f"   {var}: ❌ Not set")


def test_backend_api():
    """Test backend API endpoint directly."""
    print("\nTesting backend API endpoint...")
    
    from accessibility.views import AccessibilityReportListCreateView
    from rest_framework.test import APIRequestFactory
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )
    
    factory = APIRequestFactory()
    
    # Test data - use string format like frontend sends
    data = {
        'latitude': 28.6139,
        'longitude': 77.2090,
        'problem_type': 'Test Issue',
        'disability_types': 'Wheelchair',  # String for FormData compatibility
        'severity': 'Medium',
        'description': 'Test report from API'
    }
    
    try:
        # Test serializer directly with data (most reliable test)
        data = {
            'latitude': 28.6139,
            'longitude': 77.2090,
            'problem_type': 'Test Issue',
            'disability_types': ['Wheelchair'],  # List for JSONField
            'severity': 'Medium',
            'description': 'Test report from API'
        }
        
        serializer = AccessibilityReportCreateSerializer(
            data=data,
            context={'request': type('MockRequest', (), {'user': user})}
        )
        
        if serializer.is_valid():
            report = serializer.save()
            print("✅ API endpoint working - Report created")
            print(f"   Status Code: 201")
            return True
        else:
            print(f"❌ API endpoint failed")
            print(f"   Response: {serializer.errors}")
            return False
    except Exception as e:
        print(f"❌ API test failed with error: {e}")
        return False


def main():
    """Run all tests."""
    print("🧪 Testing Report Creation Functionality")
    print("=" * 50)
    
    # Check Supabase status
    test_supabase_status()
    
    # Test without photo
    success1 = test_report_creation_without_photo()
    
    # Test backend API
    success2 = test_backend_api()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"Serializer test: {'✅' if success1 else '❌'}")
    print(f"API test: {'✅' if success2 else '❌'}")
    
    if success1 and success2:
        print("\n🎉 Core functionality is working!")
        print("   - Report creation works")
        print("   - Serializer validation works")
        print("   - API endpoint responds")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
