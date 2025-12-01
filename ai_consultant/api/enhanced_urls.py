"""
🌐 Enhanced AI API URLs
Advanced AI endpoints with RAG integration and recommendations
"""

from django.urls import path
from ai_consultant.api import enhanced_views

urlpatterns = [
    # 🚀 Enhanced AI Chat API
    path('enhanced-chat/', enhanced_views.EnhancedAIChatView.as_view(), name='enhanced_ai_chat'),

    # 📚 RAG Management
    path('rag/rebuild-index/', enhanced_views.rebuild_rag_index, name='rebuild_rag_index'),

    # 🎯 Recommendations API
    path('recommendations/', enhanced_views.get_recommendations_api, name='get_recommendations'),
    path('recommendations/rate/', enhanced_views.rate_club_recommendation, name='rate_recommendation'),

    # 🏥 Health Check
    path('health/', enhanced_views.health_check, name='ai_health_check'),

    # 📊 Analytics and Monitoring
    path('analytics/interactions/', enhanced_views.get_interaction_analytics, name='interaction_analytics'),
    path('analytics/performance/', enhanced_views.get_performance_metrics, name='performance_metrics'),
]