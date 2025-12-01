"""
🎯 Простые URL-ы для облегченной системы

Этот файл содержит только необходимые URL-ы для облегченной системы.
"""

from django.urls import path
from ai_consultant.api.lightweight_api import (
    LightweightAgentView,
    get_club_creation_guide_view,
    get_categories_info_view,
    get_creation_stats_view,
    validate_club_data_view,
    health_check
)

urlpatterns = [
    # 🤖 Main lightweight agent endpoint
    path('agent/', LightweightAgentView.as_view(), name='lightweight_agent'),

    # 📚 Guide and information
    path('guide/', get_club_creation_guide_view, name='lightweight_guide'),
    path('categories/', get_categories_info_view, name='lightweight_categories'),

    # 📊 Statistics
    path('stats/', get_creation_stats_view, name='lightweight_stats'),

    # ✅ Validation
    path('validate/', validate_club_data_view, name='lightweight_validate'),

    # 🏥 Health check
    path('health/', health_check, name='health_check'),
]