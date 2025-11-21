"""
🏗️ ИИ-консультант v2.0 - Рефакторинговая архитектура
Разделение монолитного сервиса на специализированные компоненты
"""

import os
import json
import logging
from typing import List, Dict, Optional, Any
from abc import ABC, abstractmethod
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone
from openai import OpenAI

from .models import ChatSession, ChatMessage, AIContext
from .services.base import BaseAIService
from .services.chat import ChatService
from .services.context import ContextService
from .services.openai_client import OpenAIClientService
from .utils.logging import AIConsultantLogger
from .services.message_processor import MessageProcessorService
from .services.club_creation import ClubCreationService
from .services.club_management import ClubManagementService
from .services.feedback import FeedbackService
from .services.platform import PlatformServiceManager
from .services.interview import InterviewStudioService
from clubs.services import ClubRecommendationService
from .services.development import DevelopmentRecommendationService
from .services.knowledge import KnowledgeBaseService
from .services.rag_service import get_rag_service
from .services.enhanced_context import get_enhanced_context_service
from .services.enhanced_analytics import get_enhanced_analytics_service


User = get_user_model()
logger = logging.getLogger(__name__)


class AIConsultantServiceV2:
    """
    🚀 Основной сервис ИИ-консультанта v2.0 - Enhanced with RAG
    Координирует работу специализированных сервисов с RAG и предиктивной аналитикой
    """

    VERSION = "2.1.0"  # Обновленная версия с RAG
    BUILD_DATE = "2025-11-20"

    def __init__(self):
        # 🤖 OpenAI клиент
        self.openai_service = OpenAIClientService()

        # 💬 Основные сервисы
        self.chat_service = ChatService(self.openai_service, service_provider=self)
        self.context_service = ContextService()
        self.message_processor = MessageProcessorService()
        self.club_creation_service = ClubCreationService()
        self.club_management_service = ClubManagementService()
        self.feedback_service = FeedbackService()
        self.platform_service_manager = PlatformServiceManager()
        self.interview_studio_service = InterviewStudioService()
        self.recommendation_service = ClubRecommendationService()
        self.development_service = DevelopmentRecommendationService()
        self.knowledge_service = KnowledgeBaseService()

        # 🔍 RAG и улучшенные сервисы
        self.rag_service = get_rag_service()
        self.enhanced_context_service = get_enhanced_context_service()
        self.enhanced_analytics_service = get_enhanced_analytics_service()

        # 📊 Кэширование
        self.cache_timeout = getattr(settings, 'AI_CACHE_TIMEOUT', 300)  # 5 минут

        logger.info(f"ИИ-консультант v{self.VERSION} с RAG инициализирован")

    def log_info(self, message: str, extra: Dict = None):
        """Логирование информационных сообщений"""
        if extra:
            logger.info(f"{message} | {extra}")
        else:
            logger.info(message)

    def log_error(self, message: str, extra: Dict = None):
        """Логирование ошибок"""
        if extra:
            logger.error(f"{message} | {extra}")
        else:
            logger.error(message)

    def create_chat_session(self, user: User) -> ChatSession:
        """
        Создает новую сессию чата
        """
        try:
            session = self.chat_service.create_session(user)
            self.log_info(f"Создана новая сессия чата", {'session_id': session.id, 'user_id': user.id})
            return session
        except Exception as e:
            self.log_error(f"Ошибка создания сессии чата: {e}")
            raise

    def send_message(self, session: ChatSession, message: str) -> Dict[str, Any]:
        """
        🚀 Основной метод отправки сообщения с RAG и улучшенным контекстом
        """
        try:
            # 🔍 Предварительная обработка сообщения
            processed_message = self.message_processor.preprocess(message)
            self.log_info(f"Обработка сообщения", {'session_id': session.id, 'length': len(processed_message)})

            # 🧠 Получение улучшенного контекста с RAG
            enhanced_context = self.enhanced_context_service.get_enhanced_session_context(
                session_id=str(session.id),
                user_message=processed_message
            )

            if enhanced_context.get('error'):
                self.log_warning(f"Проблемы с RAG контекстом", {'error': enhanced_context['error']})
                # Используем стандартный контекст как запасной вариант
                enhanced_context = self._get_fallback_enhanced_context(session, processed_message)

            # 💬 Отправка в чат сервис с улучшенным контекстом
            response_data = self.chat_service.send_message(
                session=session,
                message=processed_message,
                context_service=self.context_service,
                enhanced_context=enhanced_context  # Передача улучшенного контекста
            )

            # 📊 Постобработка ответа
            processed_response = self.message_processor.postprocess(response_data['response'])

            # 📈 Запись аналитики
            self._record_interaction_analytics(session, processed_message, processed_response, enhanced_context)

            # 🧹 Очистка старых сообщений
            self._cleanup_old_messages(session)

            # 🔄 Обновление RAG индекса при необходимости
            self._update_rag_index_if_needed(session, processed_message, processed_response)

            self.log_info(f"Сообщение обработано с RAG", {
                'session_id': session.id,
                'user_messages': session.messages.filter(role='user').count(),
                'ai_messages': session.messages.filter(role='assistant').count(),
                'rag_confidence': enhanced_context.get('rag_context', {}).get('overall_confidence', 0),
                'predictions': enhanced_context.get('predictions', {})
            })

            return {
                'response': processed_response,
                'session_id': session.id,
                'message_id': response_data.get('message_id'),
                'tokens_used': response_data.get('tokens_used', 0),
                'enhanced_context': {
                    'rag_confidence': enhanced_context.get('rag_context', {}).get('overall_confidence', 0),
                    'predictions': enhanced_context.get('predictions', {}),
                    'personalization': enhanced_context.get('personalization', {})
                }
            }

        except Exception as e:
            self.log_error(f"Ошибка обработки сообщения с RAG: {e}")
            return self._get_fallback_response()

    def get_user_sessions(self, user: User) -> List[Dict]:
        """
        Получает список сессий пользователя
        """
        return self.chat_service.get_user_sessions(user)

    def get_chat_history(self, session: ChatSession, limit: int = 50, offset: int = 0) -> List[Dict]:
        """
        Получает историю чата с пагинацией

        Args:
            session: Сессия чата
            limit: Лимит сообщений (по умолчанию 50)
            offset: Смещение для пагинации (по умолчанию 0)

        Returns:
            List[Dict]: Список сообщений чата
        """
        try:
            # Для пагинации не используем кэш, т.к. offset часто меняется
            # В будущем можно реализовать более умное кэширование
            if offset == 0:  # Только для первой страницы используем кэш
                cache_key = f"chat_history_{session.id}_{limit}"
                cached_history = cache.get(cache_key)

                if cached_history:
                    self.log_info(f"История чата загружена из кэша", {'session_id': session.id})
                    return cached_history

            # Получаем историю с учетом offset
            history = self.chat_service.get_history(session, limit + offset)

            # Применяем offset
            if offset > 0:
                history = history[offset:]

            # Ограничиваем количество сообщений
            history = history[:limit]

            # Кэшируем только первую страницу
            if offset == 0:
                cache_key = f"chat_history_{session.id}_{limit}"
                cache.set(cache_key, history, self.cache_timeout)

            self.log_info(f"Загружена история чата", {
                'session_id': session.id,
                'messages_count': len(history),
                'limit': limit,
                'offset': offset,
                'cached': offset == 0
            })

            return history

        except Exception as e:
            self.log_error(f"Ошибка получения истории чата: {e}")
            return []

    def get_chat_messages_count(self, session: ChatSession) -> int:
        """
        Получает общее количество сообщений в чате

        Args:
            session: Сессия чата

        Returns:
            int: Количество сообщений
        """
        try:
            # Проверяем кэш
            cache_key = f"chat_messages_count_{session.id}"
            cached_count = cache.get(cache_key)

            if cached_count is not None:
                return cached_count

            # Получаем количество из chat_service
            count = self.chat_service.get_messages_count(session)

            # Кэшируем результат
            cache.set(cache_key, count, self.cache_timeout // 2)  # Кэшируем на меньшее время

            self.log_info(f"Получено количество сообщений", {
                'session_id': session.id,
                'count': count
            })

            return count

        except Exception as e:
            self.log_error(f"Ошибка получения количества сообщений: {e}")
            return 0

    def delete_session(self, session: ChatSession) -> bool:
        """
        Удаляет сессию чата
        """
        try:
            success = self.chat_service.delete_session(session)
            if success:
                # Очистка кэша
                cache.delete_many([f"chat_history_{session.id}_*"])
                self.log_info(f"Сессия чата удалена", {'session_id': session.id})
            return success
        except Exception as e:
            self.log_error(f"Ошибка удаления сессии: {e}")
            return False

    def get_services_by_type(self, service_type: str) -> List[Dict]:
        """
        Получает услуги определенного типа
        """
        services = self.platform_service_manager.get_services_by_type(service_type)

        return [
            {
                'id': str(service.id),
                'title': service.title,
                'description': service.description,
                'price_info': service.price_info,
                'contact_info': service.contact_info
            }
            for service in services
        ]

    def get_session_stats(self, session: ChatSession) -> Dict[str, Any]:
        """
        Получает статистику сессии
        """
        try:
            stats = self.chat_service.get_session_stats(session)
            self.log_info(f"Статистика сессии получена", {'session_id': session.id, 'stats': stats})
            return stats
        except Exception as e:
            self.log_error(f"Ошибка получения статистики: {e}")
            return {}

    def update_system_context(self, category: str, content: str, is_active: bool = True) -> bool:
        """
        Обновляет системный контекст
        """
        try:
            success = self.context_service.update_context(category, content, is_active)
            if success:
                # Очистка кэша контекста
                cache.delete("system_context_*")
                self.log_info(f"Системный контекст обновлен", {'category': category})
            return success
        except Exception as e:
            self.log_error(f"Ошибка обновления контекста: {e}")
            return False

    def get_analytics_data(self, user: User) -> Dict[str, Any]:
        """
        Получает аналитические данные пользователя
        """
        try:
            cache_key = f"user_analytics_{user.id}"
            cached_analytics = cache.get(cache_key)

            if cached_analytics:
                return cached_analytics

            analytics = self.chat_service.get_user_analytics(user)
            cache.set(cache_key, analytics, self.cache_timeout * 2)  # Дольше кэшируем аналитику

            return analytics

        except Exception as e:
            self.log_error(f"Ошибка получения аналитики: {e}")
            return {}

    # 🔧 Вспомогательные методы

    def create_interview_request(self, user: User, data: Dict) -> Dict:
        """
        Создает заявку на интервью
        """
        return self.interview_studio_service.create_interview_request(user, data)

    def get_club_recommendations_for_user(self, user: User, limit: int = 5) -> Dict:
        """
        Получает персональные рекомендации клубов для пользователя
        """
        try:
            recommendations = self.recommendation_service.get_club_recommendations_for_user(user, limit)

            if not recommendations:
                # Если персональных рекомендаций нет, возвращаем популярные клубы
                popular_clubs = self.recommendation_service.get_popular_clubs(limit)
                return {
                    'success': True,
                    'type': 'popular',
                    'message': f'Пока у меня нет персональных рекомендаций для вас, но вот самые популярные клубы на платформе:',
                    'clubs': [
                        {
                            'id': str(club.id),
                            'name': club.name,
                            'description': club.description[:200] + '...' if len(club.description) > 200 else club.description,
                            'category': club.category.name if club.category else 'Без категории',
                            'members_count': club.members_count,
                            'reasons': ['Популярный клуб']
                        }
                        for club in popular_clubs
                    ]
                }

            # Формируем персональные рекомендации
            club_list = []
            for rec in recommendations:
                club = rec['club']
                club_list.append({
                    'id': str(club.id),
                    'name': club.name,
                    'description': club.description[:200] + '...' if len(club.description) > 200 else club.description,
                    'category': club.category.name if club.category else 'Без категории',
                    'members_count': club.members_count,
                    'reasons': rec['match_reasons']
                })

            return {
                'success': True,
                'type': 'personalized',
                'message': f'На основе ваших интересов я подобрал для вас эти клубы:',
                'clubs': club_list
            }

        except Exception as e:
            self.log_error(f"Error getting club recommendations: {str(e)}")
            return {
                'success': False,
                'error': 'Не удалось получить рекомендации клубов'
            }

    def get_clubs_by_interest_keywords(self, message: str, limit: int = 5) -> Dict:
        """
        Находит клубы по ключевым словам в сообщении пользователя
        """
        try:
            # Анализируем сообщение на предмет интересов
            # Создаем временный объект пользователя с интересами из сообщения
            temp_user = type('User', (), {'profile': type('Profile', (), {
                'interests': message,
                'about': '',
                'goals_for_life': ''
            })()})()
            
            interests = self.recommendation_service.analyze_user_interests(temp_user)

            if not interests:
                # Если интересы не определены, ищем по ключевым словам в названиях/описании
                from django.db.models import Q
                from clubs.models import Club
                
                clubs = Club.objects.filter(
                    is_active=True,
                    is_private=False
                ).filter(
                    Q(name__icontains=message) |
                    Q(description__icontains=message) |
                    Q(tags__icontains=message)
                ).order_by('-members_count')[:limit]

                return {
                    'success': True,
                    'type': 'keyword_search',
                    'message': f'Нашел клубы по запросу "{message}":',
                    'clubs': [
                        {
                            'id': str(club.id),
                            'name': club.name,
                            'description': club.description[:200] + '...' if len(club.description) > 200 else club.description,
                            'category': club.category.name if club.category else 'Без категории',
                            'members_count': club.members_count,
                            'reasons': ['Найдено по ключевым словам']
                        }
                        for club in clubs
                    ]
                }

            # Используем рекомендации по интересам
            scored_clubs = self.recommendation_service.find_clubs_by_interests(interests, limit * 2)

            club_list = []
            for rec in scored_clubs[:limit]:
                club = rec['club']
                club_list.append({
                    'id': str(club.id),
                    'name': club.name,
                    'description': club.description[:200] + '...' if len(club.description) > 200 else club.description,
                    'category': club.category.name if club.category else 'Без категории',
                    'members_count': club.members_count,
                    'reasons': rec['match_reasons']
                })

            return {
                'success': True,
                'type': 'interest_based',
                'message': f'По вашим интересам я нашел следующие клубы:',
                'clubs': club_list
            }

        except Exception as e:
            self.log_error(f"Error finding clubs by keywords: {str(e)}")
            return {
                'success': False,
                'error': 'Не удалось найти клубы по запросу'
            }

    def format_club_recommendations(self, recommendations_data: Dict) -> str:
        """
        Форматирует рекомендации клубов для ответа ИИ
        """
        if not recommendations_data['success']:
            return "К сожалению, я не нашел подходящих клубов. Попробуйте описать ваши интересы подробнее."

        intro = recommendations_data['message']
        clubs_text = []

        for i, club in enumerate(recommendations_data['clubs'], 1):
            club_text = f"\n🏠 **{i}. {club['name']}**\n"
            club_text += f"📝 {club['description']}\n"
            club_text += f"🏷️ Категория: {club['category']}\n"
            club_text += f"👥 Участников: {club['members_count']}\n"

            if club['reasons']:
                club_text += f"✨ Почему рекомендую: {', '.join(club['reasons'])}\n"

            clubs_text.append(club_text)

        response = intro + ''.join(clubs_text)

        # Добавляем призыв к действию
        response += "\n\n💡 **Хотите узнать подробнее о каком-то клубе или помочь вам с вступлением?**"

        return response

    def get_development_recommendations_for_user(self, user: User, message: str = '') -> Dict:
        """
        Получает рекомендации по развитию
        """
        return self.development_service.get_development_recommendations(user, message)

    def get_user_development_progress(self, user: User) -> Dict:
        """
        Получает прогресс развития пользователя
        """
        return self.development_service.get_user_development_progress(user)

    def create_development_plan_for_user(self, user: User, path_id: str) -> Dict:
        """
        Создает план развития для пользователя
        """
        return self.development_service.create_development_plan(user, path_id)

    def _cleanup_old_messages(self, session: ChatSession, keep_last: int = 100):
        """
        Очистка старых сообщений
        """
        try:
            messages_count = session.messages.count()
            if messages_count > keep_last:
                old_messages = session.messages.order_by('created_at')[:messages_count - keep_last]
                deleted_count = old_messages.count()
                old_messages.delete()
                self.log_info(f"Удалены старые сообщения", {
                    'session_id': session.id,
                    'deleted_count': deleted_count
                })
        except Exception as e:
            self.log_error(f"Ошибка очистки старых сообщений: {e}")

    def _get_fallback_response(self) -> Dict[str, Any]:
        """
        Запасной ответ при ошибках
        """
        return {
            'response': '🤖 Извините, произошла техническая ошибка. Пожалуйста, попробуйте еще раз через несколько минут.',
            'session_id': None,
            'message_id': None,
            'tokens_used': 0,
            'error': True
        }

    def log_warning(self, message: str, extra: Dict = None):
        """Логирование предупреждений"""
        if extra:
            logger.warning(f"{message} | {extra}")
        else:
            logger.warning(message)

    def _get_fallback_enhanced_context(self, session: ChatSession, message: str) -> Dict[str, Any]:
        """Запасной контекст при ошибках RAG"""
        return {
            'session_id': str(session.id),
            'user': self._get_basic_user_context(session.user),
            'message_count': session.messages.count(),
            'recent_messages': [],
            'rag_context': {'retrieved_info': {}, 'overall_confidence': 0.0},
            'predictions': {},
            'personalization': {},
            'intent_analysis': {'primary_intent': 'general', 'confidence': 0.5}
        }

    def _get_basic_user_context(self, user: User) -> Optional[Dict[str, Any]]:
        """Базовый контекст пользователя"""
        if not user:
            return None
        return {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }

    def _record_interaction_analytics(self, session: ChatSession, user_message: str, ai_response: str, enhanced_context: Dict[str, Any]):
        """Запись аналитики взаимодействия"""
        try:
            analytics_data = {
                'session_id': str(session.id),
                'user_id': session.user.id if session.user else None,
                'timestamp': timezone.now().isoformat(),
                'message_length': len(user_message),
                'response_length': len(ai_response),
                'rag_confidence': enhanced_context.get('rag_context', {}).get('overall_confidence', 0),
                'intent': enhanced_context.get('intent_analysis', {}).get('primary_intent', 'general'),
                'sentiment': enhanced_context.get('current_message', {}).get('sentiment', 'neutral')
            }
            cache_key = f"interaction_analytics_{session.id}_{timezone.now().timestamp()}"
            cache.set(cache_key, analytics_data, timeout=86400)
        except Exception as e:
            self.log_warning(f"Ошибка записи аналитики: {e}")

    def _update_rag_index_if_needed(self, session: ChatSession, user_message: str, ai_response: str):
        """Обновление RAG индекса при необходимости"""
        try:
            messages_count = session.messages.count()
            if messages_count >= 4 and messages_count % 2 == 0:
                if len(user_message) > 20 and len(ai_response) > 50:
                    conversation_text = f"Пользователь: {user_message}\nАссистент: {ai_response}"
                    metadata = {
                        'session_id': str(session.id),
                        'message_count': messages_count,
                        'document_type': 'chat_history',
                        'created_at': timezone.now().isoformat(),
                        'auto_indexed': True
                    }
                    self.rag_service.add_document('history', conversation_text, metadata)
                    self.log_info(f"Диалог добавлен в RAG индекс", {'session_id': session.id})
        except Exception as e:
            self.log_warning(f"Ошибка обновления RAG индекса: {e}")

    def get_comprehensive_analytics(self, period: str = 'week', user_id: Optional[int] = None) -> Dict[str, Any]:
        """📈 Получение комплексной аналитики"""
        try:
            return self.enhanced_analytics_service.get_comprehensive_analytics(period, user_id)
        except Exception as e:
            self.log_error(f"Ошибка получения аналитики: {e}")
            return {'error': str(e), 'timestamp': timezone.now().isoformat()}

    def rebuild_knowledge_index(self):
        """🔄 Перестроение индекса знаний"""
        try:
            self.rag_service.rebuild_index()
            self.log_info("Индекс знаний перестроен")
            return {'status': 'success', 'timestamp': timezone.now().isoformat()}
        except Exception as e:
            self.log_error(f"Ошибка перестроения индекса: {e}")
            return {'status': 'error', 'error': str(e)}

    # 🧪 Методы для тестирования и разработки

    def get_platform_services(self) -> List[Dict]:
        """
        Получает список доступных услуг платформы
        """
        services = self.platform_service_manager.get_all_services()
        return [
            {
                'id': str(service.id),
                'title': service.title,
                'type': service.get_service_type_display(),
                'service_type': service.service_type,
                'description': service.description,
                'price_info': service.price_info,
                'contact_info': service.contact_info
            }
            for service in services
        ]

    def health_check(self) -> Dict[str, Any]:
        """
        Проверка работоспособности сервиса
        """
        try:
            checks = {
                'openai_connection': self.openai_service.is_available(),
                'chat_service': self.chat_service.health_check(),
                'context_service': self.context_service.health_check(),
                'cache_available': cache.has_key('health_check_test') or self._test_cache()
            }

            overall_status = all(checks.values())
            self.log_info(f"Health check выполнен", {'status': overall_status, 'checks': checks})

            return {
                'status': 'healthy' if overall_status else 'unhealthy',
                'version': self.VERSION,
                'build_date': self.BUILD_DATE,
                'checks': checks,
                'timestamp': self._get_timestamp()
            }

        except Exception as e:
            self.log_error(f"Ошибка health check: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': self._get_timestamp()
            }

    def _test_cache(self) -> bool:
        """Тестирование кэша"""
        try:
            cache.set('health_check_test', 'test_value', 10)
            result = cache.get('health_check_test') == 'test_value'
            cache.delete('health_check_test')
            return result
        except:
            return False

    def _get_timestamp(self) -> str:
        """Получение временной метки"""
        from django.utils import timezone
        return timezone.now().isoformat()

    # 🔄 Методы для миграции с v1

    def migrate_from_v1(self, old_service):
        """
        Миграция данных со старой версии сервиса
        """
        try:
            self.log_info("Начало миграции с v1")
            # Здесь можно добавить логику миграции
            self.log_info("Миграция с v1 завершена")
            return True
        except Exception as e:
            self.log_error(f"Ошибка миграции: {e}")
            return False


# 🎯 Фабрика сервисов для удобного создания

class AIServiceFactory:
    """
    Фабрика для создания AI сервисов
    """

    @staticmethod
    def create_chat_service(user: User = None) -> AIConsultantServiceV2:
        """Создает основной сервис чата"""
        return AIConsultantServiceV2()

    @staticmethod
    def create_chat_service_only() -> ChatService:
        """Создает только чат сервис"""
        return ChatService(OpenAIClientService())

    @staticmethod
    def create_context_service() -> ContextService:
        """Создает сервис контекста"""
        return ContextService()

    @staticmethod
    def create_message_processor() -> MessageProcessorService:
        """Создает процессор сообщений"""
        return MessageProcessorService()


# 🌍 Глобальные функции для обратной совместимости

def create_ai_consultant_service() -> AIConsultantServiceV2:
    """
    Создает экземпляр AI консультант сервиса
    """
    return AIServiceFactory.create_chat_service()


def get_ai_service_health() -> Dict[str, Any]:
    """
    Получает статус здоровья AI сервисов
    """
    try:
        service = create_ai_consultant_service()
        return service.health_check()
    except Exception as e:
        logger.error(f"Ошибка получения статуса AI сервисов: {e}")
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': None
        }