"""
Простой API для чата без сложных зависимостей
Гарантированно работает с виджетом
"""

import json
import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from ai_consultant.models import ChatSession, ChatMessage
from ai_consultant.services.chat import ChatService
import uuid

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def simple_chat_session_create(request):
    """
    Создать новую сессию чата - упрощенная версия
    """
    try:
        # Создаем простую сессию
        session = ChatSession.objects.create(
            user=request.user if request.user.is_authenticated else None
        )

        return Response({
            'id': str(session.id),
            'created_at': session.created_at.isoformat(),
            'message_count': 0
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"Simple session creation error: {str(e)}")
        return Response({
            'error': 'Failed to create session'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def simple_chat_message(request):
    """
    Отправить сообщение и получить ответ - упрощенная версия
    """
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        session_id = data.get('session_id')

        if not message:
            return Response({
                'error': 'Message is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Получаем или создаем сессию
        if session_id:
            try:
                session = ChatSession.objects.get(id=session_id)
            except ChatSession.DoesNotExist:
                session = ChatSession.objects.create(
                    user=request.user if request.user.is_authenticated else None
                )
        else:
            session = ChatSession.objects.create(
                user=request.user if request.user.is_authenticated else None
            )

        # Сохраняем сообщение пользователя
        user_message = ChatMessage.objects.create(
            session=session,
            role='user',
            content=message
        )

        # Получаем ответ от AI
        try:
            chat_service = ChatService()
            ai_response = chat_service.send_message(session.id, message)
            response_text = ai_response.get('response', 'Извините, произошла ошибка. Попробуйте еще раз.')
        except Exception as ai_error:
            logger.warning(f"AI service error: {ai_error}")
            # Fallback ответ
            response_text = get_fallback_response(message)

        # Сохраняем ответ AI
        ai_message = ChatMessage.objects.create(
            session=session,
            role='assistant',
            content=response_text
        )

        return Response({
            'response': response_text,
            'session_id': str(session.id),
            'message_id': str(ai_message.id)
        }, status=status.HTTP_200_OK)

    except json.JSONDecodeError:
        return Response({
            'error': 'Invalid JSON'
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Simple chat error: {str(e)}")
        return Response({
            'error': 'Internal server error',
            'response': 'Извините, произошла ошибка. Попробуйте еще раз.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_fallback_response(message):
    """
    Получить запасной ответ, когда AI недоступен
    """
    message_lower = message.lower()

    if any(greeting in message_lower for greeting in ['привет', 'здравствуй', 'hello', 'hi']):
        return """👋 Привет! Я AI-консультант платформы ЦЕНТР СОБЫТИЙ.

Я могу помочь вам:
🔍 Найти интересные клубы и сообщества
📚 Узнать о функциях платформы
🎯 Развивать свои навыки
💡 Получить советы по созданию контента

Чем могу помочь?"""

    elif any(word in message_lower for word in ['клуб', 'сообщество', 'найти']):
        return """🔍 Поиск клубов и сообществ:

На нашей платформе вы найдете:
📚 Образовательные клубы
🎨 Творческие сообщества
💻 IT и технологические клубы
🏃 Спортивные объединения
🎵 Музыкальные коллективы

Какой тип клуба вас интересует?"""

    elif any(word in message_lower for word in ['создать', 'основать', 'начать']):
        return """🚀 Создание клуба:

Чтобы создать клуб, нужно:
1. Определить тематику и цели
2. Написать описание
3. Создать правила сообщества
4. Привлечь первых участников

Хотите подробную инструкцию?"""

    elif any(word in message_lower for word in ['помощь', 'help', 'функции', 'возможности']):
        return """💡 Возможности платформы:

✨ Создание и управление клубами
📝 Публикация событий и новостей
💬 Обсуждения и форумы
👥 Поиск единомышленников
📊 Аналитика и статистика

Что именно вас интересует?"""

    else:
        return """🤔 Я понимаю ваш вопрос.

Чтобы лучше помочь, не могли бы вы уточнить:
- Что именно вас интересует?
- Это касается клубов, событий или функций платформы?
- Вам нужна помощь с поиском или созданием чего-то?

Я здесь, чтобы помочь! 😊"""