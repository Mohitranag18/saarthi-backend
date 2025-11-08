#!/usr/bin/env python
"""
Test script to verify Supabase storage integration.
Run this script to test if Supabase storage is properly configured.
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

from accessibility.storage import supabase_storage
from django.conf import settings


def create_test_image():
    """Create a simple test image for upload testing."""
    # Create a simple 100x100 red image
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    # Create a file-like object
    from django.core.files.uploadedfile import SimpleUploadedFile
    return SimpleUploadedFile(
        "test_image.jpg",
        img_bytes.getvalue(),
        content_type="image/jpeg"
    )


def test_supabase_configuration():
    """Test if Supabase is properly configured."""
    print("Testing Supabase configuration...")
    
    # Check environment variables
    required_vars = ['SUPABASE_URL', 'SUPABASE_KEY', 'SUPABASE_BUCKET_NAME']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please add these to your .env file:")
        for var in missing_vars:
            if var == 'SUPABASE_URL':
                print(f"{var}=your-supabase-project-url")
            elif var == 'SUPABASE_KEY':
                print(f"{var}=your-supabase-anon-key")
            elif var == 'SUPABASE_BUCKET_NAME':
                print(f"{var}=saarthi-reports")
        return False
    
    print("✅ All required environment variables are set")
    
    # Test storage service initialization
    if supabase_storage.is_configured():
        print("✅ Supabase storage service is properly initialized")
        return True
    else:
        print("❌ Supabase storage service failed to initialize")
        return False


def test_file_upload():
    """Test file upload to Supabase."""
    print("\nTesting file upload...")
    
    if not supabase_storage.is_configured():
        print("❌ Cannot test upload: Supabase not configured")
        return False
    
    try:
        # Create test image
        test_file = create_test_image()
        print("✅ Test image created")
        
        # Upload file
        file_url = supabase_storage.upload_file(test_file, "test/test_upload.jpg")
        
        if file_url:
            print(f"✅ File uploaded successfully: {file_url}")
            return True
        else:
            print("❌ File upload failed")
            return False
            
    except Exception as e:
        print(f"❌ Upload test failed with error: {e}")
        return False


def test_file_deletion():
    """Test file deletion from Supabase."""
    print("\nTesting file deletion...")
    
    if not supabase_storage.is_configured():
        print("❌ Cannot test deletion: Supabase not configured")
        return False
    
    try:
        # First upload a file
        test_file = create_test_image()
        file_url = supabase_storage.upload_file(test_file, "test/test_delete.jpg")
        
        if file_url:
            print("✅ File uploaded for deletion test")
            
            # Now delete it
            deleted = supabase_storage.delete_file("test/test_delete.jpg")
            
            if deleted:
                print("✅ File deleted successfully")
                return True
            else:
                print("❌ File deletion failed")
                return False
        else:
            print("❌ Cannot test deletion: Upload failed")
            return False
            
    except Exception as e:
        print(f"❌ Deletion test failed with error: {e}")
        return False


def main():
    """Run all tests."""
    print("🧪 Testing Supabase Storage Integration")
    print("=" * 50)
    
    # Test configuration
    config_ok = test_supabase_configuration()
    
    if not config_ok:
        print("\n❌ Configuration test failed. Please fix the issues above and try again.")
        sys.exit(1)
    
    # Test upload (only if configuration is OK)
    upload_ok = test_file_upload()
    
    # Test deletion (only if upload worked)
    if upload_ok:
        deletion_ok = test_file_deletion()
    else:
        deletion_ok = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"Configuration: {'✅' if config_ok else '❌'}")
    print(f"Upload: {'✅' if upload_ok else '❌'}")
    print(f"Deletion: {'✅' if deletion_ok else '❌'}")
    
    if config_ok and upload_ok and deletion_ok:
        print("\n🎉 All tests passed! Supabase storage is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
