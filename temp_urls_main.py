"""🎯 Temporary Main URLs without AI dependencies"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Основные приложения
    path('', include('clubs.urls')),
    path('events/', include('events.urls')),
    path('users/', include('users.urls')),

    # AI Agent (lightweight, standalone)
    path('api/v1/ai/production/', include('ai_consultant.api.production_urls')),
]

# Статические файлы
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
