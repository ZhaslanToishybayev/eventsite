"""
🌐 Главные URL-ы для облегченной системы

Только основные маршруты без тяжелых AI компонентов.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # 📊 Admin panel
    path('admin/', admin.site.urls),

    # 🚀 Simple API endpoints
    path('api/v1/', include('core.simple_api_urls')),

    # 🏠 Main application (без AI компонентов)
    path('', lambda request: {
        'message': 'UnitySphere Lightweight System',
        'status': 'active',
        'features': ['Club Creation Agent', 'Validation', 'Progress Tracking'],
        'endpoints': {
            'ai_agent': '/api/v1/ai/club-creation/agent/',
            'guide': '/api/v1/ai/club-creation/guide/',
            'categories': '/api/v1/ai/club-creation/categories/',
            'validate': '/api/v1/ai/club-creation/validate/',
            'health': '/api/v1/ai/health/'
        }
    }),
]

# Static files
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)