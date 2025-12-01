"""📋 Minimal Django URLs - Только основные приложения"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Только основные приложения без проблемных зависимостей
    path('', include('clubs.urls')),
    path('accounts/', include('accounts.urls')),
]

# Статические файлы
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)