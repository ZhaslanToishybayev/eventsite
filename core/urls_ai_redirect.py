# 🔧 ПРОБЛЕМА: НУЖНО ПЕРЕКЛЮЧИТЬСЯ НА УЛУЧШЕННЫЙ AI

## 📊 **ТЕКУЩАЯ СИТУАЦИЯ:**

### ❌ **Что происходит:**
- AI консультант использует старый endpoint: `/api/v1/ai/chat/`
- Используется старая логика без функций создания клубов
- AI не может выполнять реальные действия
- Ответы слишком общие, не учитывают конкретный запрос

### ✅ **Что должно быть:**
- Использовать новый endpoint: `/api/v1/ai/enhanced/chat/`
- Использовать ActionableAIConsultant с функциями
- AI должен создавать реальные клубы в базе данных
- Ответы должны быть персонализированными и конкретными

## 🚀 **КАК ИСПРАВИТЬ:**

### **1. Проверим текущий API endpoint:**
```bash
# Текущий (старый):
curl -X POST https://fan-club.kz/api/v1/ai/chat/

# Новый (улучшенный):
curl -X POST https://fan-club.kz/api/v1/ai/enhanced/chat/
```

### **2. Обновим JavaScript виджета:**
Нужно изменить URL в `ai-chat-widget-v2.js`:

```javascript
// Старый URL:
const apiUrl = '/api/v1/ai/';

// Новый URL:
const apiUrl = '/api/v1/ai/enhanced/';
```

### **3. Обновим Django URLs:**
Нужно перенаправить `/api/v1/ai/chat/` на новый эндпоинт.

## 🔧 **ТЕХНИЧЕСКОЕ РЕШЕНИЕ:**

### **1. Создадим redirect на новый endpoint:**

<tool_call>
<function=Write>
<parameter=content>
"""
🔧 REDIRECT НА УЛУЧШЕННЫЙ AI ENDPOINT
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from django.conf import settings

# Импортируем улучшенный AI агент
from actionable_ai_consultant import ActionableAIConsultant

@csrf_exempt
def redirect_to_enhanced_ai(request):
    """Перенаправление на улучшенный AI endpoint"""
    return JsonResponse({
        'status': 'redirect',
        'message': 'This endpoint has been moved to /api/v1/ai/enhanced/chat/',
        'new_endpoint': '/api/v1/ai/enhanced/chat/',
        'features': [
            'real_club_creation',
            'event_planning',
            'club_management',
            'monetization_advice',
            'personalized_responses'
        ]
    })

@csrf_exempt
def enhanced_ai_chat_redirect(request):
    """Улучшенный AI chat с функциями (новый endpoint)"""
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
                'timestamp': '2025-11-25T09:30:00',
                'message_id': hash(message + str('2025-11-25T09:30:00')),
                'features_enabled': [
                    'club_creation',
                    'event_planning',
                    'personalization',
                    'real_time_actions'
                ]
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