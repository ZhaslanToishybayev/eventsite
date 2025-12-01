"""
Actionable AI Consultant API - для реального создания клубов
"""
from django.urls import path
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from actionable_ai_consultant import ActionableAIConsultant
from datetime import datetime

def actionable_ai_status(request):
    """Actionable AI API status"""
    return JsonResponse({
        'status': 'working',
        'features': ['real_club_creation', 'real_event_creation', 'database_operations', 'form_parsing'],
        'model': 'gpt-4o-mini',
        'version': '3.0',
        'capabilities': ['text_generation', 'club_creation', 'event_planning', 'database_management']
    })

@csrf_exempt
def actionable_ai_chat(request):
    """Actionable AI chat endpoint - может реально создавать клубы!"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            user_email = data.get('user_email', None)

            # Валидация входных данных
            if not message:
                return JsonResponse({
                    'error': 'Сообщение не может быть пустым'
                }, status=400)

            if len(message) > 2000:
                return JsonResponse({
                    'error': 'Сообщение слишком длинное (максимум 2000 символов)'
                }, status=400)

            # Создаем экземпляр ActionableAIConsultant
            ai = ActionableAIConsultant()

            # Обрабатываем сообщение
            response = ai.process_user_message(message, user_email)

            return JsonResponse({
                'message': response,
                'type': 'text',
                'timestamp': datetime.now().isoformat(),
                'message_id': hash(message + str(datetime.now()))
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

urlpatterns = [
    path('actionable/status/', actionable_ai_status, name='actionable_ai_status'),
    path('actionable/chat/', actionable_ai_chat, name='actionable_ai_chat'),
]