import logging
import json
from datetime import datetime
from django.utils import timezone

logger = logging.getLogger('ai_consultant')

class AIConsultantLogger:
    """
    Утилита для структурированного логирования событий AI консультанта
    """
    
    @staticmethod
    def _format_log_data(event_type: str, **kwargs) -> str:
        """Форматирует данные в JSON строку"""
        data = {
            'event': event_type,
            'timestamp': timezone.now().isoformat(),
            **kwargs
        }
        return json.dumps(data, ensure_ascii=False)

    @classmethod
    def log_request(cls, user_id: str, session_id: str, message_length: int, message_type: str = 'text'):
        """Логирование входящего запроса"""
        log_msg = cls._format_log_data(
            'ai_request',
            user_id=str(user_id),
            session_id=str(session_id),
            message_length=message_length,
            message_type=message_type
        )
        logger.info(log_msg)

    @classmethod
    def log_response(cls, session_id: str, tokens_used: int, response_time_ms: float, status: str = 'success'):
        """Логирование ответа AI"""
        log_msg = cls._format_log_data(
            'ai_response',
            session_id=str(session_id),
            tokens_used=tokens_used,
            response_time_ms=response_time_ms,
            status=status
        )
        logger.info(log_msg)

    @classmethod
    def log_error(cls, session_id: str, error_type: str, error_message: str, context: dict = None):
        """Логирование ошибок"""
        log_msg = cls._format_log_data(
            'ai_error',
            session_id=str(session_id) if session_id else None,
            error_type=error_type,
            error_message=error_message,
            context=context or {}
        )
        logger.error(log_msg)

    @classmethod
    def log_action(cls, user_id: str, action_type: str, details: dict = None):
        """Логирование действий пользователя"""
        log_msg = cls._format_log_data(
            'user_action',
            user_id=str(user_id),
            action_type=action_type,
            details=details or {}
        )
        logger.info(log_msg)
