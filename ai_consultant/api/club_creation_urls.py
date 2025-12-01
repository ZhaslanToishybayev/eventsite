"""
Club Creation Agent API URLs
"""
from django.urls import path
from ai_consultant.api.club_creation_agent_api import (
    ClubCreationAgentView,
    get_club_creation_guide,
    get_categories_info,
    validate_club_data,
    get_creation_stats
)

urlpatterns = [
    # 🤖 Main club creation agent endpoint
    path('agent/', ClubCreationAgentView.as_view(), name='club_creation_agent'),

    # 📚 Additional API endpoints
    path('guide/', get_club_creation_guide, name='club_creation_guide'),
    path('categories/', get_categories_info, name='categories_info'),
    path('validate/', validate_club_data, name='validate_club_data'),
    path('stats/', get_creation_stats, name='creation_stats'),
]