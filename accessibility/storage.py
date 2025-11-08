import os
import uuid
from typing import Optional
from django.conf import settings
from django.core.files.base import ContentFile
from supabase import create_client, Client
import logging

logger = logging.getLogger(__name__)


class SupabaseStorageService:
    """
    Service for handling file uploads to Supabase Storage.
    """
    
    def __init__(self):
        self.supabase_url: str = os.environ.get('SUPABASE_URL')
        self.supabase_key: str = os.environ.get('SUPABASE_KEY')
        self.supabase_service_role_key: str = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
        self.bucket_name: str = os.environ.get('SUPABASE_BUCKET_NAME', 'saarthi-reports')
        
        if not all([self.supabase_url, self.supabase_key]):
            logger.warning("Supabase configuration missing. File uploads will fail.")
            self.client = None
        else:
            try:
                # Use service role key for admin operations
                self.client: Client = create_client(
                    self.supabase_url,
                    self.supabase_service_role_key or self.supabase_key
                )
                logger.info("Supabase client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
                self.client = None
    
    def is_configured(self) -> bool:
        """Check if Supabase storage is properly configured."""
        return self.client is not None
    
    def upload_file(self, file_obj, file_path: Optional[str] = None) -> Optional[str]:
        """
        Upload a file to Supabase Storage.
        
        Args:
            file_obj: File object to upload
            file_path: Optional custom path for the file
            
        Returns:
            Public URL of the uploaded file or None if upload fails
        """
        if not self.is_configured():
            logger.error("Supabase storage not configured")
            return None
        
        try:
            # Generate unique file path if not provided
            if not file_path:
                file_extension = os.path.splitext(file_obj.name)[1]
                unique_filename = f"{uuid.uuid4()}{file_extension}"
                file_path = f"reports/{unique_filename}"
            
            # Read file content
            file_content = file_obj.read()
            
            # Reset file pointer for potential reuse
            file_obj.seek(0)
            
            # Upload to Supabase
            result = self.client.storage.from_(self.bucket_name).upload(
                path=file_path,
                file=file_content,
                file_options={
                    "content-type": file_obj.content_type or "image/jpeg"
                }
            )
            
            if result.data:
                # Get public URL
                public_url = self.client.storage.from_(self.bucket_name).get_public_url(file_path)
                logger.info(f"File uploaded successfully: {public_url}")
                return public_url
            else:
                logger.error(f"Upload failed: {result}")
                return None
                
        except Exception as e:
            logger.error(f"Error uploading file to Supabase: {e}")
            return None
    
    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from Supabase Storage.
        
        Args:
            file_path: Path of the file to delete
            
        Returns:
            True if deletion successful, False otherwise
        """
        if not self.is_configured():
            logger.error("Supabase storage not configured")
            return False
        
        try:
            # Extract file path from full URL if needed
            if file_path.startswith('http'):
                # Extract path from URL
                from urllib.parse import urlparse
                parsed_url = urlparse(file_path)
                file_path = parsed_url.path.lstrip('/')
            
            result = self.client.storage.from_(self.bucket_name).remove([file_path])
            
            if result.data:
                logger.info(f"File deleted successfully: {file_path}")
                return True
            else:
                logger.error(f"Delete failed: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting file from Supabase: {e}")
            return False
    
    def get_public_url(self, file_path: str) -> Optional[str]:
        """
        Get public URL for a file in Supabase Storage.
        
        Args:
            file_path: Path of the file
            
        Returns:
            Public URL or None if error occurs
        """
        if not self.is_configured():
            logger.error("Supabase storage not configured")
            return None
        
        try:
            return self.client.storage.from_(self.bucket_name).get_public_url(file_path)
        except Exception as e:
            logger.error(f"Error getting public URL: {e}")
            return None


# Global instance
supabase_storage = SupabaseStorageService()
