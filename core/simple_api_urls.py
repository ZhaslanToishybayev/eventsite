"""
🚀 Простые API URL-ы для облегченной системы

Только основные endpoints без тяжелых зависимостей.
"""

from django.urls import path, include

urlpatterns = [
    # 🤖 Lightweight AI Agent API
    path('ai/club-creation/', include('ai_consultant.api.lightweight_urls')),

    # 🏥 Health check endpoint
    path('ai/health/', lambda request: {
        'status': 'healthy',
        'service': 'Lightweight AI System',
        'version': '1.0.0'
    }),
]