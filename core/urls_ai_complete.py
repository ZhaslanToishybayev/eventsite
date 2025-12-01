"""
🎯 Полноценные AI API маршруты - Все функции ИИ-консультанта
"""
from django.urls import path, include

urlpatterns = [
    # 🤖 Основной AI чат
    path('chat/', include('ai_consultant.api.urls')),

    # 🎯 Простые AI эндпоинты (резервные)
    path('simple-chat/', include('core.simple_api_urls_new')),

    # 📊 Статус и health check
    path('health/', include('core.simple_api_urls_new')),
    path('status/', include('core.simple_api_urls_new')),
]