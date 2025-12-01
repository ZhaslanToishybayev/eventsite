"""
🤖 УЛУЧШЕННЫЙ AI API ENDPOINT С ФУНКЦИЯМИ
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
import os
from django.conf import settings
from datetime import datetime

# Импортируем наш новый AI агент
from actionable_ai_consultant import ActionableAIConsultant

@csrf_exempt
def enhanced_ai_chat(request):
    """Улучшенный AI chat endpoint с функциями"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            user_email = data.get('user_email', None)

            # Проверяем, включен ли AI
            ai_enabled = getattr(settings, 'AI_CONSULTANT_ENABLED', False)

            if not ai_enabled:
                return JsonResponse({
                    'error': 'AI консультант временно отключен'
                }, status=503)

            # Валидация входных данных
            if not message:
                return JsonResponse({
                    'error': 'Сообщение не может быть пустым'
                }, status=400)

            if len(message) > 1000:
                return JsonResponse({
                    'error': 'Сообщение слишком длинное (максимум 1000 символов)'
                }, status=400)

            # Проверка на потенциально опасные команды
            dangerous_patterns = [
                r'drop\s+table',
                r'delete\s+from',
                r'update\s+.*\s+set.*where',
                r'insert\s+into',
                r'exec\s*\(',
                r'sp_\w+',
                r'xp_\w+',
                r'<script>',
                r'javascript:',
                r'data:text/html'
            ]

            import re
            for pattern in dangerous_patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    return JsonResponse({
                        'error': 'Недопустимое содержание сообщения'
                    }, status=400)

            # Получаем AI ответ с функциями
            ai_agent = ActionableAIConsultant()
            response = ai_agent.process_user_message(message, user_email)

            return JsonResponse({
                'message': response,
                'type': 'text',
                'timestamp': datetime.now().isoformat(),
                'message_id': hash(message + str(datetime.now())),
                'action_performed': ai_agent.get_last_action() if hasattr(ai_agent, 'get_last_action') else None
            })

        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Некорректный JSON формат'
            }, status=400)

        except Exception as e:
            return JsonResponse({
                'error': f'Ошибка обработки запроса: {str(e)}'
            }, status=500)

    return JsonResponse({
        'error': 'Только POST запросы разрешены'
    }, status=405)

def enhanced_ai_status(request):
    """Статус улучшенного AI API"""
    return JsonResponse({
        'status': 'working',
        'features': [
            'club_creation',      # Создание клубов
            'event_planning',     # Планирование мероприятий
            'club_management',    # Управление клубами
            'monetization',       # Монетизация
            'user_personalization', # Персонализация
            'real_time_actions'   # Реальные действия
        ],
        'model': 'gpt-4o-mini',
        'version': '3.0',
        'capabilities': [
            'text_generation',
            'club_creation',
            'event_planning',
            'business_consulting',
            'community_management'
        ],
        'action_templates': [
            'create_club',
            'create_event',
            'manage_club',
            'monetization_advice'
        ]
    })

# URL patterns для улучшенного AI API
enhanced_urlpatterns = [
    path('', enhanced_ai_status, name='enhanced_ai_status'),
    path('chat/', enhanced_ai_chat, name='enhanced_ai_chat'),
]