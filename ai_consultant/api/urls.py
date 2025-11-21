from django.urls import path
from . import views
from . import serena_views
from . import simple_views
from . import test_views
from . import simple_chat_api

# Import public API fixes (from root directory)
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
from api_fixes import ai_chat_public, ai_welcome_public, ai_status_public, ai_chat_debug

# Import AI Club Creator
from ai_club_creator import ai_club_creator_public

app_name = 'ai_consultant_api'

urlpatterns = [
    # Основной эндпоинт для чата (простой API для виджета)
    path('chat/', views.chat, name='chat'),

    # Простой API чата (гарантированно работает)
    path('chat-simple/', simple_chat_api.simple_chat_message, name='simple_chat'),

    # Продвинутый эндпоинт для чата (Class Based View)
    path('chat-advanced/', views.ChatAPIView.as_view(), name='chat_advanced'),

    # Управление сессиями
    path('chat/session/', views.create_chat_session, name='create_chat_session'),
    path('chat/message/', views.chat, name='chat_message'),
    path('sessions/', views.chat_sessions, name='chat_sessions'),
    path('sessions/create/', views.create_chat_session, name='create_chat_session_alt'),
    path('sessions/create-simple/', simple_chat_api.simple_chat_session_create, name='simple_session_create'),
    path('sessions/<uuid:session_id>/delete/', views.delete_chat_session, name='delete_chat_session'),

    # Публичные эндпоинты для новых посетителей
    path('welcome/', views.welcome_message, name='welcome_message'),

    # Профиль пользователя и первый визит
    path('user-profile/', views.user_profile, name='user_profile'),
    path('mark-first-visit/', views.mark_first_visit, name='mark_first_visit'),

    # Услуги платформы (общие)
    path('platform-services/', views.platform_services, name='platform_services'),
    path('health/', views.system_health_check, name='health'),
    path('services/', views.platform_services_list, name='platform_services_list'),
    path('services/<str:service_type>/', views.services_by_type, name='services_by_type'),
    path('services/search/', views.search_services, name='search_services'),
    path('services/<uuid:service_id>/similar/', views.similar_services, name='similar_services'),
    path('services/request/', views.create_service_request, name='create_service_request'),

    # Заявки на интервью
    path('interview-request/', views.create_interview_request, name='create_interview_request'),

    # Рекомендации клубов
    path('recommendations/clubs/', views.club_recommendations, name='club_recommendations'),
    path('recommendations/search/', views.search_clubs, name='search_clubs'),

    # Рекомендации по развитию
    path('recommendations/development/', views.development_recommendations, name='development_recommendations'),
    path('development/paths/', views.development_paths, name='development_paths'),
    path('development/progress/', views.development_progress, name='development_progress'),
    path('development/plan/create/', views.create_development_plan, name='create_development_plan'),

    # Помощь в создании клубов
    path('club-creation/ideas/', views.club_creation_ideas, name='club_creation_ideas'),
    path('club-creation/names/', views.club_name_suggestions, name='club_name_suggestions'),
    path('club-creation/description/', views.club_description_generator, name='club_description_generator'),
    path('club-creation/monetization/', views.club_monetization_ideas, name='club_monetization_ideas'),
    path('club-creation/plan/', views.club_action_plan, name='club_action_plan'),

    # Обратная связь
    path('feedback/', views.create_feedback, name='create_feedback'),
    path('feedback/categories/', views.feedback_categories, name='feedback_categories'),
    path('feedback/history/', views.feedback_history, name='feedback_history'),
    path('feedback/rate/', views.rate_feedback, name='rate_feedback'),
    path('feedback/statistics/', views.feedback_statistics, name='feedback_statistics'),

    # Студия интервью
    path('interview/', views.create_interview_request, name='create_interview_request'),
    path('interview/types/', views.interview_types, name='interview_types'),
    path('interview/requests/', views.user_interview_requests, name='user_interview_requests'),
    path('interview/preparation/', views.interview_preparation_guide, name='interview_preparation_guide'),
    path('interview/statistics/', views.interview_statistics, name='interview_statistics'),

    # Статистика
    path('statistics/', views.chat_statistics, name='chat_statistics'),

    # Serena AI интеграция
    path('serena/status/', serena_views.serena_status, name='serena_status'),
    path('serena/analyze/', serena_views.serena_analyze_code, name='serena_analyze_code'),
    path('serena/symbol/', serena_views.serena_search_symbol, name='serena_search_symbol'),
    path('serena/symbols/', serena_views.serena_list_symbols, name='serena_list_symbols'),
    path('serena/project/', serena_views.serena_project_info, name='serena_project_info'),

    # Упрощенные эндпоинты для тестирования
    path('simple-chat/', simple_views.simple_chat, name='simple_chat'),
    path('simple-welcome/', simple_views.simple_welcome, name='simple_welcome'),
    path('simple-status/', simple_views.simple_status, name='simple_status'),

    # Тестовые эндпоинты
    path('test-chat/', test_views.test_chat, name='test_chat'),
    path('test-welcome/', test_views.test_welcome, name='test_welcome'),

    # Публичные эндпоинты (исправления CSRF/аутентификации)
    path('chat-public/', ai_chat_public, name='chat_public'),
    path('welcome-public/', ai_welcome_public, name='welcome_public'),
    path('status-public/', ai_status_public, name='status_public'),
    path('debug/', ai_chat_debug, name='debug'),

    # Интерактивный создатель клубов
    path('club-creator/', ai_club_creator_public, name='ai_club_creator'),
]