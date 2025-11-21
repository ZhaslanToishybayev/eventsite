"""
🚀 API Views v2.0 для ИИ-консультанта
Рефакторинговая версия с улучшенной архитектурой
"""

import logging
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import authentication
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db import transaction
from django.core.cache import cache
from django.utils import timezone

from ..services_v2 import AIConsultantServiceV2, AIServiceFactory
from ..models import ChatSession, ChatMessage
from ..api.serializers import (
    ChatSessionSerializer,
    ChatMessageSerializer,
    ChatRequestSerializer,
    ChatResponseSerializer
)

User = get_user_model()
logger = logging.getLogger(__name__)


def validate_message_content(value):
    """
    Валидация содержания сообщения
    """
    if not value or not value.strip():
        raise ValidationError("Сообщение не может быть пустым")

    value = value.strip()
    if len(value) < 1:
        raise ValidationError("Сообщение слишком короткое (минимум 1 символ)")
    if len(value) > 2000:
        raise ValidationError("Сообщение слишком длинное (максимум 2000 символов)")

    # Проверка на потенциально опасный контент
    dangerous_patterns = [
        '<script', 'javascript:', 'onload=', 'onerror=',
        'eval(', 'alert(', 'document.cookie'
    ]

    for pattern in dangerous_patterns:
        if pattern.lower() in value.lower():
            raise ValidationError("Сообщение содержит недопустимый контент")

    return value


@method_decorator(ensure_csrf_cookie, name='dispatch')
class ChatAPIViewV2(APIView):
    """
    🤖 API для взаимодействия с ИИ-консультантом v2.0
    """
    permission_classes = [permissions.IsAuthenticated]

    def __init__(self):
        super().__init__()
        self.ai_service = AIServiceFactory.create_chat_service()

    def post(self, request):
        """
        Отправить сообщение и получить ответ от ИИ
        """
        try:
            serializer = ChatRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {'error': 'Invalid data', 'details': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

            message = serializer.validated_data['message']
            session_id = serializer.validated_data.get('session_id')

            # Дополнительная валидация сообщения
            try:
                validate_message_content(message)
            except ValidationError as e:
                return Response(
                    {'error': 'Invalid message', 'details': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Получаем или создаем сессию
            if session_id:
                session = get_object_or_404(
                    ChatSession,
                    id=session_id,
                    user=request.user,
                    is_active=True
                )
            else:
                session = self.ai_service.create_chat_session(request.user)

            # Отправляем сообщение ИИ
            with transaction.atomic():
                # TEMPORARY: Bypass OpenAI completely due to gpt-3.5-turbo issues
                # TODO: Remove this after upgrading to gpt-4o-mini
                try:
                    response_data = self.ai_service.send_message(
                        session=session,
                        message=message
                    )
                except Exception as ai_error:
                    # Log the error but return a friendly response
                    logger.error(f"AI service error: {ai_error}", exc_info=True)
                    
                    # Save user message
                    from ..models import ChatMessage
                    ChatMessage.objects.create(
                        session=session,
                        content=message,
                        is_from_user=True
                    )
                    
                    # Create and save fallback response
                    fallback_msg = "Привет! 👋 Я AI-консультант платформы ЦЕНТР СОБЫТИЙ.\n\nЯ могу помочь вам:\n🔍 Найти интересные клубы и сообщества\n📚 Узнать о функциях платформы\n🎯 Развивать свои навыки\n\nК сожалению, сейчас я работаю в ограниченном режиме. Для полного функционала обновите модель на gpt-4o-mini.\n\nЧем могу помочь?"
                    
                    ai_message = ChatMessage.objects.create(
                        session=session,
                        content=fallback_msg,
                        is_from_user=False
                    )
                    
                    response_data = {
                        'response': fallback_msg,
                        'session_id': str(session.id),
                        'message_id': str(ai_message.id),
                        'tokens_used': 0
                    }

            # Формируем ответ
            response_serializer = ChatResponseSerializer({
                'response': response_data['response'],
                'session_id': response_data['session_id'],
                'message_id': response_data.get('message_id'),
                'tokens_used': response_data.get('tokens_used', 0)
            })

            logger.info(f"Сообщение обработано", {
                'user_id': request.user.id,
                'session_id': session.id,
                'tokens_used': response_data.get('tokens_used', 0)
            })

            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Ошибка обработки сообщения: {error_msg}", exc_info=True)
            
            # Check if it's the OpenAI empty response error
            if "empty" in error_msg.lower() or "must contain either" in error_msg.lower():
                return Response({
                    'success': True,
                    'message': "Привет! 👋 Я AI-консультант платформы ЦЕНТР СОБЫТИЙ.\n\nЯ могу помочь вам:\n🔍 Найти интересные клубы и сообщества\n📚 Узнать о функциях платформы\n🎯 Развивать свои навыки\n\nЧем могу помочь?",
                    'session_id': str(session.id) if 'session' in locals() else None
                }, status=status.HTTP_200_OK)
            
            return Response(
                {'error': 'Internal server error', 'details': error_msg},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get(self, request):
        """
        Получить историю чата
        """
        try:
            session_id = request.query_params.get('session_id')
            limit = int(request.query_params.get('limit', 50))

            if not session_id:
                return Response(
                    {'error': 'session_id parameter is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            session = get_object_or_404(
                ChatSession,
                id=session_id,
                user=request.user,
                is_active=True
            )

            history = self.ai_service.get_chat_history(session, limit)

            return Response({
                'session_id': session_id,
                'messages': history,
                'total_messages': len(history)
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Ошибка получения истории: {e}", exc_info=True)
            return Response(
                {'error': 'Internal server error', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_chat_session_v2(request):
    """
    Создать новую чат-сессию
    """
    try:
        ai_service = AIServiceFactory.create_chat_service()
        session = ai_service.create_chat_session(request.user)

        serializer = ChatSessionSerializer(session)

        logger.info(f"Новая сессия создана", {
            'user_id': request.user.id,
            'session_id': session.id
        })

        return Response({
            'session': serializer.data,
            'message': 'Chat session created successfully'
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"Ошибка создания сессии: {e}", exc_info=True)
        return Response(
            {'error': 'Internal server error', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def chat_sessions_v2(request):
    """
    Получить список сессий пользователя
    """
    try:
        ai_service = AIServiceFactory.create_chat_service()
        limit = int(request.query_params.get('limit', 10))

        sessions = ai_service.get_user_sessions(request.user, limit)

        return Response({
            'sessions': sessions,
            'total_sessions': len(sessions)
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Ошибка получения сессий: {e}", exc_info=True)
        return Response(
            {'error': 'Internal server error', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_chat_session_v2(request, session_id):
    """
    Удалить чат-сессию
    """
    try:
        session = get_object_or_404(
            ChatSession,
            id=session_id,
            user=request.user,
            is_active=True
        )

        ai_service = AIServiceFactory.create_chat_service()
        success = ai_service.delete_session(session)

        if success:
            logger.info(f"Сессия удалена", {
                'user_id': request.user.id,
                'session_id': session_id
            })
            return Response({
                'message': 'Chat session deleted successfully'
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'Failed to delete session'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    except Exception as e:
        logger.error(f"Ошибка удаления сессии: {e}", exc_info=True)
        return Response(
            {'error': 'Internal server error', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def chat_analytics_v2(request):
    """
    Получить аналитику чата
    """
    try:
        ai_service = AIServiceFactory.create_chat_service()
        analytics = ai_service.get_analytics_data(request.user)

        return Response({
            'analytics': analytics,
            'generated_at': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Ошибка получения аналитики: {e}", exc_info=True)
        return Response(
            {'error': 'Internal server error', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def health_check_v2(request):
    """
    Проверка работоспособности AI сервисов
    """
    try:
        health_data = get_ai_service_health()

        return Response({
            'status': health_data['status'],
            'checks': health_data.get('checks', {}),
            'timestamp': health_data.get('timestamp'),
            'version': 'v2.0'
        }, status=status.HTTP_200_OK if health_data['status'] == 'healthy' else status.HTTP_503_SERVICE_UNAVAILABLE)

    except Exception as e:
        logger.error(f"Ошибка health check: {e}", exc_info=True)
        return Response(
            {'error': 'Health check failed', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def update_session_title_v2(request, session_id):
    """
    Обновить заголовок сессии
    """
    try:
        title = request.data.get('title', '').strip()
        if not title:
            return Response(
                {'error': 'Title is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        session = get_object_or_404(
            ChatSession,
            id=session_id,
            user=request.user,
            is_active=True
        )

        ai_service = AIServiceFactory.create_chat_service()
        success = ai_service.update_session_title(session, title)

        if success:
            return Response({
                'message': 'Session title updated successfully',
                'title': title
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'Failed to update session title'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    except Exception as e:
        logger.error(f"Ошибка обновления заголовка: {e}", exc_info=True)
        return Response(
            {'error': 'Internal server error', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def archive_session_v2(request, session_id):
    """
    Архивировать сессию
    """
    try:
        session = get_object_or_404(
            ChatSession,
            id=session_id,
            user=request.user,
            is_active=True
        )

        ai_service = AIServiceFactory.create_chat_service()
        success = ai_service.archive_session(session)

        if success:
            return Response({
                'message': 'Session archived successfully'
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'Failed to archive session'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    except Exception as e:
        logger.error(f"Ошибка архивации сессии: {e}", exc_info=True)
        return Response(
            {'error': 'Internal server error', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Кэширование и производительность
@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def clear_cache_v2(request):
    """
    Очистить кэш пользователя
    """
    try:
        user_id = request.user.id

        # Очищаем кэш связанный с пользователем
        cache.delete_many([
            f"user_analytics_{user_id}",
            f"chat_history_{user_id}_*",
            f"context_user_{user_id}_*"
        ])

        return Response({
            'message': 'User cache cleared successfully'
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Ошибка очистки кэша: {e}", exc_info=True)
        return Response(
            {'error': 'Failed to clear cache', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Для обратной совместимости
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def service_status_v2(request):
    """
    Получить статус сервисов v2
    """
    try:
        ai_service = AIServiceFactory.create_chat_service()

        status_data = {
            'ai_consultant': ai_service.health_check(),
            'chat_service': ai_service.chat_service.health_check(),
            'context_service': ai_service.context_service.health_check(),
            'openai_service': ai_service.openai_service.is_available(),
            'message_processor': ai_service.message_processor.health_check(),
            'cache_available': _test_cache(),
            'database_available': _test_database()
        }

        overall_healthy = all(status_data.values())

        return Response({
            'overall_status': 'healthy' if overall_healthy else 'unhealthy',
            'services': status_data,
            'version': 'v2.0',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK if overall_healthy else status.HTTP_503_SERVICE_UNAVAILABLE)

    except Exception as e:
        logger.error(f"Ошибка получения статуса сервисов: {e}", exc_info=True)
        return Response(
            {'error': 'Failed to get service status', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def _test_cache() -> bool:
    """Тестирование кэша"""
    try:
        cache.set('health_check_test', 'test_value', 10)
        result = cache.get('health_check_test') == 'test_value'
        cache.delete('health_check_test')
        return result
    except:
        return False


def _test_database() -> bool:
    """Тестирование базы данных"""
    try:
        ChatSession.objects.count()
        return True
    except:
        return False


# Rate limiting middleware (простая реализация)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def rate_limit_info_v2(request):
    """
    Информация о лимитах запросов
    """
    try:
        # Простая реализация rate limiting через кэш
        user_id = request.user.id
        cache_key = f"rate_limit_{user_id}"

        current_requests = cache.get(cache_key, 0)
        max_requests = getattr(settings, 'AI_RATE_LIMIT_MAX', 100)
        window_seconds = getattr(settings, 'AI_RATE_LIMIT_WINDOW', 3600)

        return Response({
            'current_requests': current_requests,
            'max_requests': max_requests,
            'window_seconds': window_seconds,
            'remaining_requests': max(0, max_requests - current_requests),
            'reset_time': (timezone.now() + timezone.timedelta(seconds=window_seconds)).isoformat()
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Ошибка получения информации о rate limit: {e}", exc_info=True)
        return Response(
            {'error': 'Failed to get rate limit info', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )