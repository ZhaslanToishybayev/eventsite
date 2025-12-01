"""
📋 Enhanced AI API URLs
URL маршруты для улучшенного AI API
"""

from django.urls import path
from ai_consultant.api.enhanced_chat_api import (
    enhanced_ai_chat,
    enhanced_ai_health,
    club_search_api,
    club_categories_api,
    cities_api
)

app_name = 'enhanced_ai'

urlpatterns = [
    # Основной улучшенный AI чат
    path('enhanced/chat/', enhanced_ai_chat, name='enhanced_chat'),

    # Health check
    path('enhanced/health/', enhanced_ai_health, name='enhanced_health'),

    # API для поиска клубов
    path('enhanced/clubs/search/', club_search_api, name='club_search'),

    # API для категорий
    path('enhanced/categories/', club_categories_api, name='categories'),

    # API для городов
    path('enhanced/cities/', cities_api, name='cities'),
]