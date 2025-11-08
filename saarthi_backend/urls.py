# from django.contrib import admin  # Temporarily disabled
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # path('admin/', admin.site.urls),  # Temporarily disabled
    path('api/users/', include('users.urls')),
    path('api/', include('accessibility.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
