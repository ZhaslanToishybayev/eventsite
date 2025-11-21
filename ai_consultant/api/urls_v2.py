"""
🔗 URL конфигурация API v2.0 для ИИ-консультанта
"""

from django.urls import path
from . import views_v2

app_name = 'ai_consultant_api_v2'

urlpatterns = [
    # Основные эндпоинты чата
    path('chat/v2/', views_v2.ChatAPIViewV2.as_view(), name='chat_v2'),
    path('sessions/v2/create/', views_v2.create_chat_session_v2, name='create_chat_session_v2'),
    path('sessions/v2/', views_v2.chat_sessions_v2, name='chat_sessions_v2'),
    path('sessions/v2/<uuid:session_id>/delete/', views_v2.delete_chat_session_v2, name='delete_chat_session_v2'),
    path('sessions/v2/<uuid:session_id>/title/', views_v2.update_session_title_v2, name='update_session_title_v2'),
    path('sessions/v2/<uuid:session_id>/archive/', views_v2.archive_session_v2, name='archive_session_v2'),

    # Аналитика и статистика
    path('analytics/v2/', views_v2.chat_analytics_v2, name='chat_analytics_v2'),
    path('rate-limit/v2/', views_v2.rate_limit_info_v2, name='rate_limit_info_v2'),

    # Системные эндпоинты
    path('health/v2/', views_v2.health_check_v2, name='health_check_v2'),
    path('status/v2/', views_v2.service_status_v2, name='service_status_v2'),
    path('cache/v2/clear/', views_v2.clear_cache_v2, name='clear_cache_v2'),
]