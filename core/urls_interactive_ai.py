"""
Interactive AI Consultant API - интерактивное создание клубов
"""
from django.urls import path
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from interactive_ai_consultant import InteractiveAIConsultant
from datetime import datetime

def interactive_ai_status(request):
    """Interactive AI API status"""
    return JsonResponse({
        'status': 'working',
        'features': ['interactive_club_creation', 'step_by_step_questions', 'user_guided_creation'],
        'model': 'gpt-4o-mini',
        'version': '4.0',
        'capabilities': ['interactive_questions', 'club_creation', 'guided_process']
    })

@csrf_exempt
def interactive_ai_chat(request):
    """Interactive AI chat endpoint - задает вопросы пользователю!"""
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

            # Создаем экземпляр InteractiveAIConsultant
            ai = InteractiveAIConsultant()

            # Получаем session_key из запроса или создаем новый
            print(f"DEBUG: Endpoint - before session_key check")
            session_key = request.session.session_key
            print(f"DEBUG: Endpoint - session_key before: {session_key}")

            # Убедимся, что сессия активна
            if not session_key:
                print(f"DEBUG: Endpoint - creating new session")
                request.session.create()
                session_key = request.session.session_key
                print(f"DEBUG: Endpoint - created new session_key: {session_key}")
            else:
                print(f"DEBUG: Endpoint - using existing session_key: {session_key}")

            # Обрабатываем сообщение
            response = ai.process_user_message(message, user_email, session_key)

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
    path('interactive/status/', interactive_ai_status, name='interactive_ai_status'),
    path('interactive/chat/', interactive_ai_chat, name='interactive_ai_chat'),
]