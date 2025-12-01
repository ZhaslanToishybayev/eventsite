"""🎯 Production URLs - Lightweight AI Agent Only"""
from django.urls import path, include

urlpatterns = [
    # 🚀 Production AI Agent endpoints
    path('api/v1/ai/production/', include('ai_consultant.api.production_urls')),

    # 🌐 Main site URLs (clubs, events, etc.)
    path('', include('clubs.urls')),
    path('events/', include('events.urls')),
    path('users/', include('users.urls')),

    # 📊 Health check endpoint
    path('health/', include('core.urls_health')),
]