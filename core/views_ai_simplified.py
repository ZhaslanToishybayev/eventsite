"""
Simplified AI Views for UnitySphere
"""
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import logging

logger = logging.getLogger(__name__)

def ai_consultant_page(request):
    """AI Consultant page"""
    return render(request, 'ai_consultant/chat.html')

def ai_status_api(request):
    """AI status endpoint"""
    return JsonResponse({
        'status': 'disabled',
        'message': 'AI функции временно отключены',
        'features': [
            'Базовый сайт работает',
            'Регистрация пользователей',
            'Управление клубами',
            'Поиск клубов'
        ]
    })
