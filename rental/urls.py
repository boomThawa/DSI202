# rental/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('rentalapp.urls')),  # เชื่อมกับ rentalapp
    
    path('accounts/', include('django.contrib.auth.urls')),  # ✅ เพิ่มบรรทัดนี้
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# เสิร์ฟไฟล์ Media ในโหมดพัฒนา
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)