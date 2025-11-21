# 🔧 НЕМЕДЛЕННЫЕ ИСПРАВЛЕНИЯ API

# Проблема: test-view декоратор конфликтует с методом класса
# Решение: Декоратор @csrf_exempt для view-based эндпоинтов

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.decorators.debug import sensitive_post_parameters
import json
import time
import uuid
# Simple AI response generation
def generate_ai_response(message):
    """
    Простая генерация AI ответа на основе ключевых слов
    """
    message_lower = message.lower()

    if 'создать клуб' in message_lower or 'создание клуба' in message_lower:
        return """Чтобы создать клуб на платформе:

1. Войдите в свой аккаунт
2. Нажмите "Создать клуб"
3. Заполните:
   - Название
   - Описание
   - Категорию
   - Загрузите логотип
4. Опубликуйте клуб

Я могу помочь составить описание. Напишите "помоги с описанием клуба\""""

    elif 'найти клуб' in message_lower or 'клубы' in message_lower:
        return """На платформе уже есть несколько клубов:

1. Художественная Палитра - для художников
2. Вершинные Скалолазы - для альпинистов
3. Книжные Вдохновители - для любителей литературы
4. Танцующие Экстазы - для танцоров

Какой клуб вас интересует?"""

    elif 'помощь' in message_lower or 'help' in message_lower:
        return """Я могу помочь вам:
* Создать новый клуб
* Найти существующие клубы
* Рассказать о функциях платформы
* Дать советы по развитию

Что вас интересует?"""

    elif 'привет' in message_lower or 'здравствуй' in message_lower:
        return """Привет! Я AI-ассистент платформы "Центр Событий".

Чем я могу вам помочь сегодня?
* Создать клуб
* Найти сообщество
* Узнать о платформе"""

    else:
        return f"""Я получил ваше сообщение: "{message}"

Я AI-ассистент и могу помочь:
* Создать клуб
* Найти клубы
* Получить помощь

Попробуйте спросить "помощь" или "создать клуб\""""

@csrf_exempt
@require_http_methods(["GET", "POST"])
@sensitive_post_parameters()
def ai_chat_public(request):
    """
    Публичный API эндпоинт для AI чата без аутентификации
    Исправляет проблемы с CSRF и правами доступа
    """
    start_time = time.time()

    if request.method == 'GET':
        return JsonResponse({
            'message': 'AI Chat Public API - POST only',
            'endpoint': '/api/v1/ai/chat-public/',
            'methods': ['POST'],
            'authentication': 'Not required'
        })

    if request.method == 'POST':
        try:
            # Получаем данные из request
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST.dict()

            message = data.get('message', '').strip()

            if not message:
                return JsonResponse({
                    'error': 'Message is required',
                    'success': False
                }, status=400)

            # Генерируем AI ответ
            ai_response = generate_ai_response(message)

            response_data = {
                'success': True,
                'message': ai_response,
                'response': ai_response,
                'session_id': str(uuid.uuid4()),
                'message_id': str(uuid.uuid4()),
                'tokens_used': 0,
                'processing_time': f"{time.time() - start_time:.2f}s",
                'fallback_mode': True,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }

            return JsonResponse(response_data)

        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON data',
                'success': False
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'error': f'Internal error: {str(e)}',
                'success': False
            }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def ai_welcome_public(request):
    """
    Публичный эндпоинт для приветствия
    """
    return JsonResponse({
        'message': 'AI Assistant Public API',
        'suggestions': [
            'Создать клуб',
            'Найти клубы',
            'Платформа помощь'
        ],
        'status': 'working',
        'fallback_mode': True,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    })

@csrf_exempt
@require_http_methods(["GET"])
def ai_status_public(request):
    """
    Публичный эндпоинт для статуса
    """
    return JsonResponse({
        'status': 'working',
        'mode': 'public_fallback',
        'api_version': 'v1.0',
        'features': [
            'Chat processing',
            'Club creation assistance',
            'Club search',
            'Platform help',
            'Security filtering'
        ],
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    })

# CSRF-less testing endpoint (для отладки)
@csrf_exempt
@require_http_methods(["POST"])
def ai_chat_debug(request):
    """
    Debug endpoint без проверок безопасности (ТОЛЬКО ДЛЯ ОТЛАДКИ!)
    """
    start_time = time.time()

    try:
        data = json.loads(request.body) if request.body else {}
        message = data.get('message', '').strip()

        if not message:
            return JsonResponse({
                'error': 'Message is required',
                'success': False
            }, status=400)

        # Генерируем AI ответ
        ai_response = generate_ai_response(message)

        response_data = {
            'success': True,
            'message': ai_response,
            'processing_time': f"{time.time() - start_time:.2f}s",
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'debug_mode': True
        }

        return JsonResponse(response_data)

    except Exception as e:
        return JsonResponse({
            'error': f'Debug error: {str(e)}',
            'success': False,
            'traceback': str(e)
        }, status=500)