"""
Максимально простой тестовый API
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_ratelimit.decorators import ratelimit
from django.views.decorators.csrf import csrf_exempt
import time
import uuid


@api_view(['POST'])
@permission_classes([AllowAny])
@ratelimit(key='ip', rate='30/m', method='POST', block=True)
@csrf_exempt
def test_chat(request):
    """
    Максимально простой тестовый чат
    """
    start_time = time.time()

    try:
        # Получаем данные из запроса
        data = request.data
        message = data.get('message', '').strip()
        session_id = data.get('session_id')

        # Базовая проверка
        if not message:
            return Response({
                'error': 'Message is required',
                'success': False
            }, status=400)

        # Генерируем простой ответ
        message_lower = message.lower()

        if 'создать клуб' in message_lower or 'создание клуба' in message_lower:
            ai_response = """Чтобы создать клуб на платформе:

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
            ai_response = """На платформе уже есть несколько клубов:

1. Художественная Палитра - для художников
2. Вершинные Скалолазы - для альпинистов
3. Книжные Вдохновители - для любителей литературы
4. Танцующие Экстазы - для танцоров

Какой клуб вас интересует?"""

        elif 'помощь' in message_lower or 'help' in message_lower:
            ai_response = """Я могу помочь вам:
* Создать новый клуб
* Найти существующие клубы
* Рассказать о функциях платформы
* Дать советы по развитию

Что вас интересует?"""

        elif 'привет' in message_lower or 'здравствуй' in message_lower:
            ai_response = """Привет! Я AI-ассистент платформы "Центр Событий".

Чем я могу вам помочь сегодня?
* Создать клуб
* Найти сообщество
* Узнать о платформе"""

        else:
            ai_response = f"""Я получил ваше сообщение: "{message}"

Я AI-ассистент и могу помочь:
* Создать клуб
* Найти клубы
* Получить помощь

Попробуйте спросить "помощь" или "создать клуб\""""

        # Возвращаем успешный ответ
        return Response({
            'success': True,
            'message': ai_response,
            'response': ai_response,
            'session_id': session_id or str(uuid.uuid4()),
            'message_id': str(uuid.uuid4()),
            'tokens_used': 0,
            'processing_time': f"{time.time() - start_time:.2f}s",
            'fallback_mode': True
        })

    except Exception as e:
        # Возвращаем ошибку
        return Response({
            'error': f'Error: {str(e)}',
            'success': False,
            'message': 'Произошла ошибка. Попробуйте еще раз.'
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def test_welcome(request):
    """Тестовое приветствие"""
    return Response({
        'message': 'AI ассистент платформы Центр Событий',
        'suggestions': [
            'Создать клуб',
            'Найти клубы',
            'Помощь'
        ],
        'status': 'working'
    })