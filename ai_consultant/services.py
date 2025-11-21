"""
🔧 Сервисы ИИ консультанта с персистентными сессиями
"""

import json
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple

from django.utils import timezone
from django.db import transaction
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ObjectDoesNotExist

from .models import ConversationState, AISessionLog, ClubCreationRequest
from .security import log_security_event

logger = logging.getLogger(__name__)


class ConversationStateService:
    """
    💾 Сервис для управления персистентными состояниями对话
    """

    def __init__(self):
        self.default_expiration_hours = 24  # 24 часа по умолчанию

    def get_or_create_state(self, session_id: str, user=None,
                          user_agent: str = None, ip_address: str = None) -> ConversationState:
        """
        Получить или создать состояние对话

        Args:
            session_id: ID сессии
            user: Пользователь (опционально)
            user_agent: User-Agent браузера (опционально)
            ip_address: IP адрес (опционально)

        Returns:
            ConversationState: Объект состояния对话
        """
        try:
            # Сначала ищем существующее состояние
            state = ConversationState.objects.get(session_id=session_id)

            # Проверяем не истекла ли сессия
            if state.is_expired:
                logger.info(f"Session {session_id} expired, creating new one")
                state = self._create_new_state(session_id, user, user_agent, ip_address)
            else:
                # Обновляем метаданные если нужно
                if user_agent and state.user_agent != user_agent:
                    state.user_agent = user_agent
                if ip_address and state.ip_address != ip_address:
                    state.ip_address = ip_address
                    state.save(update_fields=['user_agent', 'ip_address', 'updated_at'])

            return state

        except ConversationState.DoesNotExist:
            # Создаем новое состояние
            return self._create_new_state(session_id, user, user_agent, ip_address)

    def _create_new_state(self, session_id: str, user=None,
                         user_agent: str = None, ip_address: str = None) -> ConversationState:
        """Создать новое состояние对话"""
        with transaction.atomic():
            state = ConversationState.objects.create(
                session_id=session_id,
                stage='welcome',
                data={},
                progress=0,
                user=user,
                user_agent=user_agent,
                ip_address=ip_address,
                expires_at=timezone.now() + timedelta(hours=self.default_expiration_hours)
            )

            # Логируем создание состояния
            log_security_event('conversation_state_created', {
                'session_id': session_id,
                'user_id': user.id if user else None,
                'ip_address': ip_address
            })

            return state

    def update_state(self, session_id: str, stage: str = None,
                     data_updates: Dict[str, Any] = None,
                     last_question: str = None,
                     progress: int = None) -> ConversationState:
        """
        Обновить состояние对话

        Args:
            session_id: ID сессии
            stage: Новый этап (опционально)
            data_updates: Обновления для JSON данных (опционально)
            last_question: Последний вопрос (опционально)
            progress: Прогресс (опционально)

        Returns:
            ConversationState: Обновленное состояние
        """
        try:
            state = ConversationState.objects.get(session_id=session_id, is_active=True)

            # Проверяем не истекла ли сессия
            if state.is_expired:
                raise ValueError(f"Session {session_id} is expired")

            with transaction.atomic():
                if stage is not None:
                    old_stage = state.stage
                    state.stage = stage

                    # Логируем изменение этапа
                    AISessionLog.objects.create(
                        session_id=session_id,
                        log_type='state_change',
                        message=f'Stage changed from {old_stage} to {stage}',
                        stage=stage,
                        response_data={'old_stage': old_stage, 'new_stage': stage}
                    )

                if data_updates:
                    # Обновляем JSON данные
                    for key, value in data_updates.items():
                        state.set_data_field(key, value)

                    # Вызываем set_data_field сохраняет данные
                    # Поэтому не нужно дополнительно сохранять data

                if last_question:
                    state.last_question = last_question

                if progress is not None:
                    state.progress = progress
                else:
                    # Автоматически обновляем прогресс на основе этапа
                    state.update_progress()

                state.save(
                    update_fields=[
                        field for field in ['stage', 'last_question', 'progress', 'updated_at']
                        if getattr(state, field) is not None
                    ]
                )

            return state

        except ConversationState.DoesNotExist:
            # Создаем новое состояние если не найдено
            logger.warning(f"State not found for session {session_id}, creating new")
            return self._create_new_state(session_id)

    def delete_state(self, session_id: str) -> bool:
        """
        Удалить состояние对话

        Args:
            session_id: ID сессии

        Returns:
            bool: Успешно ли удалено
        """
        try:
            with transaction.atomic():
                state = ConversationState.objects.get(session_id=session_id)

                # Логируем удаление
                log_security_event('conversation_state_deleted', {
                    'session_id': session_id,
                    'stage': state.stage,
                    'data_size': len(str(state.data)) if state.data else 0
                })

                state.delete()
                return True

        except ConversationState.DoesNotExist:
            return False

    def cleanup_expired_states(self) -> int:
        """
        Очистить истекшие состояния

        Returns:
            int: Количество удаленных состояний
        """
        deleted_count = ConversationState.objects.filter(
            expires_at__lt=timezone.now()
        ).delete()[0]

        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} expired conversation states")

        return deleted_count

    def get_active_sessions_count(self) -> int:
        """Получить количество активных сессий"""
        return ConversationState.objects.filter(is_active=True).count()

    def get_session_stats(self) -> Dict[str, Any]:
        """Получить статистику по сессиям"""
        from django.db.models import Count

        stats = ConversationState.objects.aggregate(
            total=Count('id'),
            active=Count('id', filter=models.Q(is_active=True)),
            expired=Count('id', filter=models.Q(expires_at__lt=timezone.now()))
        )

        # Статистика по этапам
        stage_stats = ConversationState.objects.values('stage').annotate(
            count=Count('id')
        ).order_by('count')

        return {
            'total_sessions': stats['total'],
            'active_sessions': stats['active'],
            'expired_sessions': stats['expired'],
            'by_stage': list(stage_stats),
            'timestamp': timezone.now().isoformat()
        }


class AISessionLoggingService:
    """
    📋 Сервис для логирования сессий ИИ
    """

    def log_user_input(self, session_id: str, message: str,
                        processing_time: float = None,
                        stage: str = None,
                        ip_address: str = None,
                        user_agent: str = None):
        """Логировать ввод пользователя"""
        AISessionLog.objects.create(
            session_id=session_id,
            log_type='user_input',
            message=message,
            processing_time=processing_time,
            stage=stage,
            ip_address=ip_address,
            user_agent=user_agent
        )

    def log_ai_response(self, session_id: str, response_data: Dict[str, Any],
                        processing_time: float = None,
                        tokens_used: int = None,
                        stage: str = None,
                        ip_address: str = None):
        """Логировать ответ ИИ"""
        AISessionLog.objects.create(
            session_id=session_id,
            log_type='ai_response',
            message=response_data.get('message', ''),
            response_data=response_data,
            processing_time=processing_time,
            tokens_used=tokens_used,
            stage=stage,
            ip_address=ip_address
        )

    def log_error(self, session_id: str, error_message: str,
                    processing_time: float = None,
                    stage: str = None,
                    ip_address: str = None,
                    response_data: Dict[str, Any] = None):
        """Логировать ошибку"""
        AISessionLog.objects.create(
            session_id=session_id,
            log_type='error',
            message=error_message,
            response_data=response_data,
            processing_time=processing_time,
            stage=stage,
            ip_address=ip_address
        )

    def log_security_event(self, session_id: str, event_type: str,
                           details: Dict[str, Any],
                           processing_time: float = None):
        """Логировать событие безопасности"""
        AISessionLog.objects.create(
            session_id=session_id,
            log_type='security',
            message=f"Security event: {event_type}",
            response_data=details,
            processing_time=processing_time
        )

    def get_session_logs(self, session_id: str, limit: int = 100, offset: int = 0) -> dict:
        """
        Получить логи сессии с пагинацией

        Args:
            session_id: ID сессии
            limit: Лимит записей (по умолчанию 100, максимум 500)
            offset: Смещение для пагинации (по умолчанию 0)

        Returns:
            dict: Словарь с логами и информацией о пагинации
        """
        try:
            # Ограничиваем максимальный размер страницы
            limit = min(limit, 500)

            # Получаем общее количество записей
            total_count = AISessionLog.objects.filter(
                session_id=session_id
            ).count()

            # Получаем записи с учетом offset и limit
            logs = list(AISSessionLog.objects.filter(
                session_id=session_id
            ).order_by('-created_at')[offset:offset + limit])

            # Вычисляем информацию о пагинации
            total_pages = (total_count + limit - 1) // limit
            current_page = (offset // limit) + 1
            has_next = offset + limit < total_count
            has_prev = offset > 0

            return {
                'logs': logs,
                'pagination': {
                    'total_count': total_count,
                    'current_page': current_page,
                    'page_size': limit,
                    'total_pages': total_pages,
                    'offset': offset,
                    'has_next': has_next,
                    'has_prev': has_prev,
                    'next_offset': offset + limit if has_next else None,
                    'prev_offset': offset - limit if has_prev else None
                }
            }

        except Exception as e:
            logger.error(f"Error getting session logs: {e}")
            return {
                'logs': [],
                'pagination': {
                    'total_count': 0,
                    'current_page': 1,
                    'page_size': limit,
                    'total_pages': 0,
                    'offset': 0,
                    'has_next': False,
                    'has_prev': False,
                    'next_offset': None,
                    'prev_offset': None
                }
            }

    def get_logs_by_type(self, log_type: str, hours: int = 24) -> list:
        """Получить логи по типу за последние N часов"""
        since = timezone.now() - timedelta(hours=hours)
        return list(AISSessionLog.objects.filter(
            log_type=log_type,
            created_at__gte=since
        ).order_by('-created_at'))

    def cleanup_old_logs(self, days: int = 30) -> int:
        """
        Очистить старые логи

        Args:
            days: Количество дней для хранения

        Returns:
            int: Количество удаленных записей
        """
        cutoff_date = timezone.now() - timedelta(days=days)
        deleted_count = AISessionLog.objects.filter(
            created_at__lt=cutoff_date
        ).delete()[0]

        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} old AI session logs")

        return deleted_count


class ClubCreationTrackingService:
    """
    🏗️ Сервис для отслеживания создания клубов
    """

    def track_creation_request(self, session_state: ConversationState,
                                 club_data: Dict[str, Any]) -> ClubCreationRequest:
        """
        Отследить запрос на создание клуба

        Args:
            session_state: Состояние对话
            club_data: Данные клуба

        Returns:
            ClubCreationRequest: Объект запроса
        """
        with transaction.atomic():
            request = ClubCreationRequest.objects.create(
                session_state=session_state,
                club_name=club_data.get('name', ''),
                category=club_data.get('category', ''),
                description=club_data.get('description', ''),
                email=club_data.get('email', ''),
                phone=club_data.get('phone', ''),
                status='pending'
            )

            logger.info(f"Tracking club creation request: {club_data.get('name')} - {request.id}")
            return request

    def mark_success(self, request: ClubCreationRequest, club_id: str):
        """Отметить успешное создание"""
        request.status = 'success'
        request.club_id = club_id
        request.save(update_fields=['status', 'club_id', 'updated_at'])
        logger.info(f"Club creation successful: {request.club_name} - {club_id}")

    def mark_failed(self, request: ClubCreationRequest, error_message: str):
        """Отметить ошибку создания"""
        request.status = 'failed'
        request.error_message = error_message
        request.save(update_fields=['status', 'error_message', 'updated_at'])
        logger.warning(f"Club creation failed: {request.club_name} - {error_message}")

    def mark_cancelled(self, request: ClubCreationRequest):
        """Отметить отмену создания"""
        request.status = 'cancelled'
        request.save(update_fields=['status', 'updated_at'])
        logger.info(f"Club creation cancelled: {request.club_name}")

    def get_pending_requests(self) -> list:
        """Получить ожидающие запросы"""
        return list(ClubCreationRequest.objects.filter(status='pending').order_by('-created_at'))

    def get_creation_stats(self) -> Dict[str, Any]:
        """Получить статистику создания клубов"""
        from django.db.models import Count

        stats = ClubCreationRequest.objects.aggregate(
            total=Count('id'),
            pending=Count('id', filter=models.Q(status='pending')),
            success=Count('id', filter=models.Q(status='success')),
            failed=Count('id', filter=models.Q(status='failed')),
            cancelled=Count('id', filter=models.Q(status='cancelled'))
        )

        return {
            'total_requests': stats['total'],
            'pending_requests': stats['pending'],
            'successful_creations': stats['success'],
            'failed_attempts': stats['failed'],
            'cancelled_requests': stats['cancelled'],
            'success_rate': (
                (stats['success'] / max(stats['total'], 1)) * 100
            ) if stats['total'] > 0 else 0,
            'timestamp': timezone.now().isoformat()
        }


# Глобальные экземпляры сервисов
conversation_state_service = ConversationStateService()
session_logging_service = AISessionLoggingService()
club_creation_service = ClubCreationTrackingService()

print("🔧 AI Consultant services loaded successfully")