"""
Chat Business Service
Вынесенная бизнес-логика из ai_consultant/api/views.py
"""

import logging
import time
from typing import Dict, Any, Optional, Tuple
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework import status

from ai_consultant.services_v2 import AIConsultantServiceV2
from ai_consultant.models import ChatSession, ChatMessage
from ai_consultant.services.club_creation import ClubCreationService
from ai_consultant.services.feedback import FeedbackService
from ai_consultant.services.platform import PlatformServiceManager
from core.security import sanitize_input_data
from core.monitoring import ai_monitor

User = get_user_model()
logger = logging.getLogger(__name__)


class MessageValidator:
    """Валидатор сообщений чата"""

    @staticmethod
    def validate_message_content(value: str) -> str:
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


class ChatBusinessService:
    """
    Бизнес-логика для чата ИИ-консультанта
    """

    def __init__(self):
        self._ai_service = None
        self.validator = MessageValidator()

    @property
    def ai_service(self):
        if self._ai_service is None:
            self._ai_service = AIConsultantServiceV2()
        return self._ai_service

    def process_message(self, request_data: Dict[str, Any], user: Optional[User] = None,
                       client_ip: str = None) -> Tuple[Dict[str, Any], int]:
        """
        Обработка сообщения пользователя

        Returns:
            Tuple[response_data, status_code]
        """
        start_time = time.time()

        try:
            # 1. Валидация и очистка данных
            sanitized_data = self._sanitize_and_validate(request_data)

            # 2. Извлечение параметров
            session_id = sanitized_data.get('session_id')
            message = sanitized_data.get('message', '')

            # 3. Валидация сообщения
            self.validator.validate_message_content(message)

            # 4. Получение или создание сессии
            session = self._get_or_create_session(session_id, user)

            # 5. Отправка сообщения в AI
            response = self.ai_service.send_message(session, message)

            # 6. Формирование успешного ответа
            return self._format_success_response(response, session, start_time)

        except ValidationError as e:
            logger.warning(f"Validation error in chat: {e}")
            return self._format_error_response(str(e), status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error processing chat message: {e}")
            return self._format_error_response(
                "Произошла ошибка при обработке сообщения",
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_chat_history(self, session_id: str, user: Optional[User] = None,
                        page: int = 1, page_size: int = 50) -> Tuple[Dict[str, Any], int]:
        """
        Получение истории чата с пагинацией

        Returns:
            Tuple[response_data, status_code]
        """
        try:
            session = self._get_session_with_permission_check(session_id, user)

            # Получаем историю
            history = self.ai_service.get_chat_history(
                session, limit=page_size, offset=(page - 1) * page_size
            )

            # Получаем общее количество сообщений
            total_messages = self.ai_service.get_chat_messages_count(session)

            # Вычисляем пагинацию
            total_pages = (total_messages + page_size - 1) // page_size
            has_next = page < total_pages
            has_prev = page > 1

            response_data = {
                'history': history,
                'pagination': {
                    'current_page': page,
                    'page_size': page_size,
                    'total_messages': total_messages,
                    'total_pages': total_pages,
                    'has_next': has_next,
                    'has_prev': has_prev,
                    'next_page': page + 1 if has_next else None,
                    'prev_page': page - 1 if has_prev else None
                },
                'session_id': session_id
            }

            return response_data, status.HTTP_200_OK

        except ValidationError as e:
            return self._format_error_response(str(e), status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error getting chat history: {e}")
            return self._format_error_response(
                "Ошибка при получении истории чата",
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def create_chat_session(self, user: Optional[User] = None) -> Tuple[Dict[str, Any], int]:
        """
        Создание новой чат-сессии

        Returns:
            Tuple[response_data, status_code]
        """
        try:
            session = self.ai_service.create_session(user)

            response_data = {
                'session_id': session.id,
                'created_at': session.created_at.isoformat(),
                'is_active': session.is_active
            }

            return response_data, status.HTTP_201_CREATED

        except Exception as e:
            logger.error(f"Error creating chat session: {e}")
            return self._format_error_response(
                "Ошибка при создании сессии",
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete_chat_session(self, session_id: str, user: Optional[User] = None) -> Tuple[Dict[str, Any], int]:
        """
        Удаление чат-сессии

        Returns:
            Tuple[response_data, status_code]
        """
        try:
            session = self._get_session_with_permission_check(session_id, user)

            success = self.ai_service.delete_session(session)

            if success:
                return {'message': 'Сессия успешно удалена'}, status.HTTP_200_OK
            else:
                return self._format_error_response(
                    "Не удалось удалить сессию",
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except ValidationError as e:
            return self._format_error_response(str(e), status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error deleting chat session: {e}")
            return self._format_error_response(
                "Ошибка при удалении сессии",
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def submit_feedback(self, session_id: str, feedback_data: Dict[str, Any],
                       user: Optional[User] = None) -> Tuple[Dict[str, Any], int]:
        """
        Обратная связь по чату

        Returns:
            Tuple[response_data, status_code]
        """
        try:
            session = self._get_session_with_permission_check(session_id, user)

            feedback_service = FeedbackService()
            feedback = feedback_service.create_feedback(
                session=session,
                user=user,
                message_id=feedback_data.get('message_id'),
                rating=feedback_data.get('rating'),
                comment=feedback_data.get('comment', ''),
                feedback_type=feedback_data.get('feedback_type', 'chat')
            )

            return {
                'message': 'Спасибо за обратную связь!',
                'feedback_id': feedback.id
            }, status.HTTP_201_CREATED

        except ValidationError as e:
            return self._format_error_response(str(e), status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error submitting feedback: {e}")
            return self._format_error_response(
                "Ошибка при отправке обратной связи",
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # Вспомогательные методы

    def _sanitize_and_validate(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Очистка и базовая валидация входных данных"""
        try:
            return sanitize_input_data(request_data)
        except ValidationError as e:
            raise ValidationError(f"Security validation failed: {str(e)}")

    def _get_or_create_session(self, session_id: Optional[str], user: Optional[User]) -> ChatSession:
        """Получение или создание сессии"""
        if session_id:
            try:
                session = ChatSession.objects.get(id=session_id)
                # Проверка прав доступа
                if user and session.user and session.user != user:
                    raise ValidationError("Доступ запрещен")
                return session
            except ChatSession.DoesNotExist:
                raise ValidationError("Сессия не найдена")
        else:
            # Создание новой сессии
            return self.ai_service.create_session(user)

    def _get_session_with_permission_check(self, session_id: str, user: Optional[User]) -> ChatSession:
        """Получение сессии с проверкой прав доступа"""
        try:
            session = ChatSession.objects.get(id=session_id)

            # Проверка прав доступа
            if user and session.user and session.user != user:
                raise ValidationError("Доступ запрещен")

            return session
        except ChatSession.DoesNotExist:
            raise ValidationError("Сессия не найдена")

    def _format_success_response(self, ai_response: Dict[str, Any], session: ChatSession,
                               start_time: float) -> Tuple[Dict[str, Any], int]:
        """Формирование успешного ответа"""
        duration = time.time() - start_time

        # Записываем метрики
        ai_monitor.log_request(
            endpoint='chat',
            duration=duration,
            status='success',
            tokens_used=ai_response.get('tokens_used', 0)
        )

        response_data = {
            'response': ai_response.get('response', ''),
            'message_id': ai_response.get('message_id'),
            'session_id': session.id,
            'tokens_used': ai_response.get('tokens_used', 0),
            'agent': ai_response.get('agent', 'unknown'),
            'processing_time': round(duration, 2)
        }

        return response_data, status.HTTP_200_OK

    def _format_error_response(self, error_message: str, status_code: int) -> Tuple[Dict[str, Any], int]:
        """Формирование ответа с ошибкой"""
        return {
            'error': error_message,
            'timestamp': timezone.now().isoformat()
        }, status_code


# Глобальный экземпляр сервиса (для обратной совместимости)
chat_business_service = ChatBusinessService()