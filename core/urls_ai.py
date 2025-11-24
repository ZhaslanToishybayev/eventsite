"""
URL patterns for AI Consultant functionality
"""
from django.urls import path
from . import views_ai

urlpatterns = [
    # AI Consultant main page
    path('ai/consultant/', views_ai.ai_consultant_page, name='ai_consultant'),

    # AI API endpoints
    path('api/ai/chat/', views_ai.ai_chat_api, name='ai_chat_api'),
    path('api/ai/club-help/', views_ai.ai_club_help_api, name='ai_club_help_api'),
    path('api/ai/event-ideas/', views_ai.ai_event_ideas_api, name='ai_event_ideas_api'),
]