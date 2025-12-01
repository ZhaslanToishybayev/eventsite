"""
🤖 URLS ДЛЯ УЛУЧШЕННОГО AI С ФУНКЦИЯМИ
"""

from django.urls import path
from . import urls_ai_actionable

urlpatterns = [
    path('', urls_ai_actionable.enhanced_ai_status, name='enhanced_ai_status'),
    path('chat/', urls_ai_actionable.enhanced_ai_chat, name='enhanced_ai_chat'),
]