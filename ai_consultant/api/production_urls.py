from django.urls import path
from ai_consultant.api import production_api

urlpatterns = [
    # 🚀 Production AI Agent endpoints
    path('production/agent/', production_api.production_ai_agent, name='production_ai_agent'),
    path('production/health/', production_api.production_ai_health, name='production_ai_health'),
    path('production/info/', production_api.production_ai_info, name='production_ai_info'),

    # 🎯 Main endpoints (redirect to production)
    path('agent/', production_api.production_ai_agent, name='ai_agent'),
    path('health/', production_api.production_ai_health, name='ai_health'),
    path('info/', production_api.production_ai_info, name='ai_info'),
]