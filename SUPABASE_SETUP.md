# Supabase Storage Integration Guide

This document explains how to set up and use Supabase Storage for handling report images in the Saarthi backend.

## Overview

The Saarthi backend now supports image uploads through Supabase Storage, providing a scalable and reliable solution for storing report images. This integration allows users to upload photos when creating accessibility reports.

## Features

- ✅ Image upload to Supabase Storage buckets
- ✅ Automatic file validation (size, type)
- ✅ Unique filename generation
- ✅ Public URL generation for uploaded images
- ✅ Error handling and logging
- ✅ Graceful fallback when Supabase is not configured

## Setup Instructions

### 1. Create Supabase Project

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Create a new project or use an existing one
3. Note your project URL and anon key

### 2. Create Storage Bucket

1. In your Supabase project, go to Storage section
2. Create a new bucket named `saarthi-reports` (or your preferred name)
3. Set up appropriate CORS policies if needed
4. Configure bucket permissions for public access (for image display)

### 3. Configure Environment Variables

Add the following variables to your `.env` file:

```env
# Supabase Storage Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key
SUPABASE_BUCKET_NAME=saarthi-reports
```

**Where to find these values:**

- `SUPABASE_URL`: Your project URL from Supabase dashboard
- `SUPABASE_KEY`: Anon/public key from API settings
- `SUPABASE_SERVICE_ROLE_KEY`: Service role key from API settings (recommended for backend operations)
- `SUPABASE_BUCKET_NAME`: Name of your storage bucket (default: `saarthi-reports`)

### 4. Install Dependencies

The required dependencies are already added to `requirements.txt`:

```
supabase==2.7.0
```

Install them with:

```bash
pip install -r requirements.txt
```

## Usage

### API Endpoint

The report creation endpoint now supports image uploads:

```
POST /api/accessibility/reports/
Content-Type: multipart/form-data
```

**Request Parameters:**

- `photo`: Image file (optional)
- `latitude`: Report latitude
- `longitude`: Report longitude
- `problem_type`: Type of problem
- `disability_types`: Array of disability types
- `severity`: Severity level
- `description`: Report description

**Example Request:**

```bash
curl -X POST \
  http://localhost:8000/api/accessibility/reports/ \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: multipart/form-data' \
  -F 'photo=@path/to/image.jpg' \
  -F 'latitude=28.6139' \
  -F 'longitude=77.2090' \
  -F 'problem_type=Pothole' \
  -F 'disability_types=["Wheelchair","Mobility Issues"]' \
  -F 'severity=High' \
  -F 'description=Large pothole on main road'
```

**Response:**

```json
{
  "id": "uuid-here",
  "latitude": "28.613900",
  "longitude": "77.209000",
  "problem_type": "Pothole",
  "disability_types": ["Wheelchair", "Mobility Issues"],
  "severity": "High",
  "description": "Large pothole on main road",
  "photo_url": "https://your-project-id.supabase.co/storage/v1/object/public/saarthi-reports/reports/uuid-generated.jpg",
  "status": "Active",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z",
  "user": {
    "id": 1,
    "username": "user123",
    "email": "user@example.com"
  }
}
```

## File Upload Validation

### File Size
- Maximum file size: 10MB (configurable via `MAX_UPLOAD_SIZE` setting)

### Allowed File Types
- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- WebP (.webp)

### File Naming
- Files are automatically renamed to avoid conflicts
- Format: `reports/{uuid}.{extension}`
- Example: `reports/123e4567-e89b-12d3-a456-426614174000.jpg`

## Testing

### Run the Test Script

A test script is provided to verify your Supabase configuration:

```bash
cd saarthi-backend
python test_supabase_storage.py
```

This script will test:
1. Environment variable configuration
2. Supabase client initialization
3. File upload functionality
4. File deletion functionality

### Manual Testing

1. Start your Django development server
2. Use Postman or curl to test the report creation endpoint
3. Upload an image with the request
4. Verify the image appears in your Supabase storage bucket
5. Check that the `photo_url` in the response is accessible

## Troubleshooting

### Common Issues

1. **Missing Environment Variables**
   ```
   ERROR: Supabase configuration missing. File uploads will fail.
   ```
   **Solution:** Add all required environment variables to `.env` file

2. **Upload Failed**
   ```
   ERROR: Failed to upload photo. Please try again.
   ```
   **Solution:** Check your Supabase credentials and bucket permissions

3. **File Size Limit Exceeded**
   ```
   ERROR: File size cannot exceed 10MB
   ```
   **Solution:** Use a smaller image or increase `MAX_UPLOAD_SIZE` in settings

4. **Invalid File Type**
   ```
   ERROR: File type not allowed. Allowed types: .jpg, .jpeg, .png, .gif, .webp
   ```
   **Solution:** Convert image to one of the allowed formats

### Debug Mode

Enable debug logging by adding to your Django settings:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'accessibility.storage': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## Security Considerations

1. **Service Role Key**: Use the service role key for backend operations (has elevated permissions)
2. **Bucket Permissions**: Configure appropriate bucket policies in Supabase
3. **File Validation**: Server-side validation prevents malicious file uploads
4. **CORS**: Configure CORS policies for your bucket if accessing from web clients

## Configuration Options

You can customize the behavior through Django settings:

```python
# File upload settings
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_UPLOAD_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.webp']

# Supabase settings
SUPABASE_URL = 'your-project-url'
SUPABASE_KEY = 'your-anon-key'
SUPABASE_SERVICE_ROLE_KEY = 'your-service-role-key'
SUPABASE_BUCKET_NAME = 'your-bucket-name'
```

## Frontend Integration

For the React Native frontend, update your API calls to include image uploads:

```javascript
const formData = new FormData();
formData.append('photo', {
  uri: photoUri,
  type: 'image/jpeg',
  name: 'photo.jpg'
});
formData.append('latitude', latitude);
formData.append('longitude', longitude);
// ... other fields

const response = await fetch('/api/accessibility/reports/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'multipart/form-data',
  },
  body: formData,
});
```

## Migration from Local Storage

If you have existing reports with local image URLs, you can migrate them to Supabase:

1. Create a migration script to upload existing images
2. Update `photo_url` fields in the database
3. Remove old local files

## Support

For issues related to:
- **Supabase Storage**: Check [Supabase Documentation](https://supabase.com/docs)
- **Django Integration**: Review the code in `accessibility/storage.py`
- **API Usage**: Check the test script and examples above

## Future Enhancements

Potential improvements to consider:
- Image compression before upload
- Image thumbnails generation
- Multiple image support per report
- Image metadata extraction
- CDN integration for faster delivery
