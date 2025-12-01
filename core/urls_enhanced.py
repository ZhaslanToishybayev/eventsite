"""
🔧 ОБНОВЛЕННЫЙ ОСНОВНОЙ URLS С УЛУЧШЕННЫМ AI
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Главная страница
    path('', TemplateView.as_view(template_name='base.html'), name='home'),

    # AI Консультант (Улучшенная версия)
    path('ai/', include('core.urls_ai_enhanced_v2')),

    # Старый AI endpoint (для совместимости)
    path('api/v1/ai/', include('core.urls_ai_enhanced')),

    # Клубы
    path('clubs/', include('clubs.urls')),

    # Пользователи
    path('accounts/', include('accounts.urls')),

    # События
    path('events/', include('events.urls')),

    # Публикации
    path('publications/', include('publications.urls')),

    # API v1
    path('api/v1/', include('core.urls_api_v1')),
]

# Добавляем media файлы в development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)