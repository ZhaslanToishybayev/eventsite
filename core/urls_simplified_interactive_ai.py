"""
Simplified Interactive AI API - упрощенный endpoint без сессий
"""
from django.urls import path
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from simplified_interactive_ai import SimplifiedInteractiveAIConsultant
from datetime import datetime

# Глобальный экземпляр консультанта
simplified_ai = SimplifiedInteractiveAIConsultant()

def simplified_interactive_ai_status(request):
    """Simplified Interactive AI API status"""
    return JsonResponse({
        'status': 'working',
        'features': ['session_free', 'simplified_club_creation', 'step_by_step_questions'],
        'model': 'gpt-4o-mini',
        'version': '1.0',
        'capabilities': ['session_free_chat', 'club_creation', 'guided_process']
    })

@csrf_exempt
def simplified_interactive_ai_chat(request):
    """Simplified Interactive AI chat endpoint - без сессий!"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            user_email = data.get('user_email', None)
            state_id = data.get('state_id', None)  # ID состояния от клиента

            # Валидация входных данных
            if not message:
                return JsonResponse({
                    'error': 'Сообщение не может быть пустым'
                }, status=400)

            if len(message) > 2000:
                return JsonResponse({
                    'error': 'Сообщение слишком длинное (максимум 2000 символов)'
                }, status=400)

            # Обрабатываем сообщение
            response, new_state_id = simplified_ai.process_user_message(message, user_email, state_id)

            # Если ответ - словарь (результат создания клуба), извлекаем сообщение
            if isinstance(response, dict):
                if response.get('success'):
                    message_text = f"🎉 Отлично! Клуб '{response.get('club_name', '')}' успешно создан!\n\n" \
                                  f"📋 **Информация о клубе:**\n" \
                                  f"- **Название:** {response.get('club_name', '')}\n" \
                                  f"- **Описание:** {response.get('description', '')[:100]}...\n" \
                                  f"- **Категория:** {response.get('category', '')}\n" \
                                  f"- **Город:** {response.get('city', '')}\n\n" \
                                  f"🔗 **Ссылка на клуб:** /clubs/{response.get('club_id', '')}/\n\n" \
                                  f"Спасибо за создание нового клуба! 🎊"
                    success = True
                else:
                    message_text = f"❌ К сожалению, не удалось создать клуб: {response.get('error', 'Неизвестная ошибка')}"
                    success = False
            else:
                message_text = response
                success = True

            return JsonResponse({
                'message': message_text,
                'type': 'text',
                'timestamp': datetime.now().isoformat(),
                'message_id': hash(message + str(datetime.now())),
                'success': success,
                'state_id': new_state_id  # Возвращаем ID состояния клиенту
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
    path('simplified/interactive/status/', simplified_interactive_ai_status, name='simplified_interactive_ai_status'),
    path('simplified/interactive/chat/', simplified_interactive_ai_chat, name='simplified_interactive_ai_chat'),
]