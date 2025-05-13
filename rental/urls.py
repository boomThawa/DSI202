# /Users/thawaphorn/Desktop/dsi202-final/rental/rental/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),  # This line is crucial!
    path('', include('rentalapp.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('auth/', include('social_django.urls', namespace='social')),  # <-- บรรทัดสำคัญ

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)