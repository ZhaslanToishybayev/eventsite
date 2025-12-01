"""
🎯 Облегченный API для стабильной работы

Этот API заменяет тяжелый Enhanced API на простую версию
для стабильной работы на сервере.
"""

import os
import json
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
import logging

from ai_consultant.agents.lightweight_agent import (
    get_lightweight_agent,
    get_club_creation_guide,
    get_categories_info,
    get_creation_stats
)

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class LightweightAgentView(View):
    """🤖 Облегченный API для создания клубов"""

    def post(self, request):
        """POST /api/v1/ai/club-creation/agent/"""

        try:
            # Проверяем аутентификацию
            if not request.user.is_authenticated:
                return JsonResponse({
                    'error': 'Authentication required',
                    'message': 'Для создания клуба нужно авторизоваться'
                }, status=401)

            # Получаем данные из запроса
            try:
                data = json.loads(request.body)
                message = data.get('message', '')
                action = data.get('action', 'message')
                context = data.get('context', {})
            except json.JSONDecodeError:
                return JsonResponse({
                    'error': 'Invalid JSON',
                    'message': 'Некорректный JSON формат'
                }, status=400)

            # Проверяем сообщение
            if not message or len(message.strip()) < 2:
                return JsonResponse({
                    'error': 'Empty message',
                    'message': 'Сообщение не может быть пустым'
                }, status=400)

            # Получаем агента
            agent = get_lightweight_agent()

            # Обрабатываем сообщение
            result = agent.process_message(
                message.strip(),
                str(request.user.id)
            )

            # Возвращаем ответ
            return JsonResponse({
                'success': True,
                'response': result['response'],
                'progress': result['progress'],
                'analysis': result['analysis'],
                'timestamp': result['timestamp']
            })

        except Exception as e:
            logger.error(f"Lightweight agent error: {e}")
            return JsonResponse({
                'error': 'Internal server error',
                'message': 'Произошла ошибка при обработке запроса'
            }, status=500)

    def get(self, request):
        """GET /api/v1/ai/club-creation/agent/"""

        return JsonResponse({
            'service': 'Lightweight Club Creation Agent',
            'status': 'active',
            'features': [
                'Natural conversation',
                'Progress tracking',
                'Simple validation',
                'Category recommendations'
            ],
            'endpoints': {
                'agent': 'POST /api/v1/ai/club-creation/agent/',
                'guide': 'GET /api/v1/ai/club-creation/guide/',
                'categories': 'GET /api/v1/ai/club-creation/categories/',
                'stats': 'GET /api/v1/ai/club-creation/stats/'
            }
        })


def get_club_creation_guide_view(request):
    """GET /api/v1/ai/club-creation/guide/"""
    guide = get_club_creation_guide()
    return JsonResponse(guide)


def get_categories_info_view(request):
    """GET /api/v1/ai/club-creation/categories/"""
    categories = get_categories_info()
    return JsonResponse({'categories': categories})


def get_creation_stats_view(request):
    """GET /api/v1/ai/club-creation/stats/"""
    stats = get_creation_stats()
    return JsonResponse(stats)


@csrf_exempt
def validate_club_data_view(request):
    """POST /api/v1/ai/club-creation/validate/"""

    if not request.user.is_authenticated:
        return JsonResponse({
            'error': 'Authentication required'
        }, status=401)

    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            agent = get_lightweight_agent()

            # Валидируем данные
            validation_result = agent.validate_club_data(data)

            return JsonResponse(validation_result)

        else:
            return JsonResponse({
                'error': 'Method not allowed'
            }, status=405)

    except Exception as e:
        logger.error(f"Validation error: {e}")
        return JsonResponse({
            'error': 'Internal server error'
        }, status=500)


# Простой health check
def health_check(request):
    """GET /api/v1/ai/health/"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'Lightweight AI Club Creation',
        'timestamp': '2024-11-26T23:20:00Z',
        'version': '1.0.0-lightweight'
    })


# Импорт для URL-ов
from django.urls import path

# Обновленная URL конфигурация для lightweight агента
urlpatterns = [
    path('agent/', LightweightAgentView.as_view(), name='lightweight_agent'),
    path('guide/', get_club_creation_guide_view, name='lightweight_guide'),
    path('categories/', get_categories_info_view, name='lightweight_categories'),
    path('stats/', get_creation_stats_view, name='lightweight_stats'),
    path('validate/', validate_club_data_view, name='lightweight_validate'),
    path('health/', health_check, name='health_check'),
]