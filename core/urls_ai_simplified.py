"""
Simplified URL patterns for AI functionality
"""
from django.urls import path
from . import views_ai_simplified

urlpatterns = [
    path('ai/consultant/', views_ai_simplified.ai_consultant_page, name='ai_consultant'),
    path('api/ai/status/', views_ai_simplified.ai_status_api, name='ai_status_api'),
]
