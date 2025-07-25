"""
Main URL Configuration for the IELTS Practice Project
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path, include

# ... other imports

urlpatterns = [
    path('admin/', admin.site.urls),
    path('reading/', include('reading.urls')),
    path('listening/', include('listening.urls')),

    # ADD THIS LINE for all authentication URLs (login, logout, password reset, etc.)
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('core.urls')),
]


# This is important for serving user-uploaded files (like your audio files) during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)