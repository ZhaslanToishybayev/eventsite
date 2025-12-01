"""📋 Minimal Django URLs - Только основные приложения"""

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from core.api_views import proxy_ai_agent, proxy_ai_health, proxy_ai_info, proxy_conversational_ai_agent
from core.api_clubs_views import api_clubs, api_club_recommendation, api_ai_chat
from core.api_ai_consultant import api_ai_consult, api_ai_clubs_search, api_ai_clubs_recommend, api_ai_club_create, api_ai_health
from ai_consultant.api.enhanced_ai_urls import urlpatterns as enhanced_ai_urls
from django.shortcuts import render
from accounts.views import find_allies_view

urlpatterns = [
    path('admin/', admin.site.urls),

    # Только основные приложения без проблемных зависимостей
    path('', include('clubs.urls')),
    path('accounts/', include('accounts.urls')),

    # Страница "Единомышленники" - реальная страница вместо редиректа
    path('find-people/', find_allies_view, name='find_people'),
    path('единомышленники/', find_allies_view, name='find_allies'),

    # Страницы тестирования удалены - оставляем только основной сайт

    # AI агент прокси API endpoints
    path('api/v1/ai/production/agent/', proxy_ai_agent, name='proxy_ai_agent'),
    path('api/v1/ai/production/health/', proxy_ai_health, name='proxy_ai_health'),
    path('api/v1/ai/production/info/', proxy_ai_info, name='proxy_ai_info'),
    path('api/v1/ai/conversational/agent/', proxy_conversational_ai_agent, name='proxy_conversational_ai_agent'),

    # Новые AI Club API endpoints
    path('api/clubs/', api_clubs, name='api_clubs'),
    path('api/clubs/recommend/', api_club_recommendation, name='api_club_recommendation'),
    path('api/ai/chat/', api_ai_chat, name='api_ai_chat'),

    # AI Consultant API endpoints
    path('api/ai/consult/', api_ai_consult, name='api_ai_consult'),
    path('api/ai/clubs/search/', api_ai_clubs_search, name='api_ai_clubs_search'),
    path('api/ai/clubs/recommend/', api_ai_clubs_recommend, name='api_ai_clubs_recommend'),
    path('api/ai/club/create/', api_ai_club_create, name='api_ai_club_create'),
    path('api/ai/health/', api_ai_health, name='api_ai_health'),

    # API v1 - Clubs
    path('api/v1/', include('core.urls_api_v1')),

    # Enhanced widget test page
    path('test_enhanced_widget/', lambda request: render(request, 'test_enhanced_widget_day2.html'), name='test_enhanced_widget'),

    # Enhanced AI API endpoints
    path('api/ai/enhanced/', include(enhanced_ai_urls)),

    # Тестовая страница AI виджета
    path('test-widget/', lambda request: render(request, 'widget_test_page.html'), name='test_widget'),
    path('widget-diagnostic/', lambda request: render(request, 'widget_diagnostic.html'), name='widget_diagnostic'),
    path('test-professional-widget/', lambda request: render(request, 'test_professional_widget.html'), name='test_professional_widget'),
    path('deep-debug/', lambda request: render(request, 'deep_debug.html'), name='deep_debug'),
    path('simple-widget/', lambda request: render(request, 'simple_working_widget.html'), name='simple_widget'),

    # Allauth URLs для авторизации и регистрации
    path('accounts/', include('allauth.urls')),
]

# Статические файлы
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    # В production режиме тоже обслуживаем медиа файлы
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)