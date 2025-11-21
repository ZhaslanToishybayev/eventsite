"""
🧠 Enhanced Context Service
Улучшенный сервис контекстуализации диалогов с RAG и предиктивной аналитикой
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, deque
import re

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone
from django.db.models import Q, Count, Avg

from ..models import ChatSession, ChatMessage, AIContext
from .rag_service import get_rag_service
from ..utils.context_analyzer import ContextAnalyzer
from ..utils.predictive_engine import PredictiveEngine

User = get_user_model()
logger = logging.getLogger(__name__)


class EnhancedContextService:
    """
    🚀 Улучшенный сервис контекстуализации с RAG и ML-предиктивной аналитикой
    """

    def __init__(self):
        self.rag_service = get_rag_service()
        self.context_analyzer = ContextAnalyzer()
        self.predictive_engine = PredictiveEngine()

        # Кэши для производительности
        self.session_cache = {}
        self.user_profile_cache = {}
        self.context_cache = {}

        # История диалогов для анализа
        self.conversation_history = defaultdict(lambda: deque(maxlen=50))

        # Пороги уверенности
        self.CONFIDENCE_THRESHOLD = 0.7
        self.MAX_CONTEXT_ITEMS = 10
        self.CONTEXT_TIMEOUT = 3600  # 1 час

    def get_enhanced_session_context(self, session_id: str, user_message: str = None) -> Dict[str, Any]:
        """
        🎯 Получение улучшенного контекста сессии с RAG и предиктивной аналитикой
        """
        try:
            # Базовый контекст сессии
            base_context = self._get_base_session_context(session_id)

            if not base_context:
                logger.warning(f"⚠️ Сессия {session_id} не найдена")
                return {'error': 'Session not found'}

            # Анализ текущего сообщения
            if user_message:
                message_analysis = self.context_analyzer.analyze_message(user_message)
                base_context['current_message'] = message_analysis

            # RAG обогащение
            rag_context = self._get_rag_context(user_message or "", base_context)
            base_context['rag_context'] = rag_context

            # Предиктивная аналитика
            predictions = self._get_predictions(base_context)
            base_context['predictions'] = predictions

            # Персонализация на основе истории
            personalization = self._get_personalization(base_context)
            base_context['personalization'] = personalization

            # Определение интента и сущностей
            intent_analysis = self._analyze_intent(base_context)
            base_context['intent_analysis'] = intent_analysis

            # Формирование итогового промпта
            enhanced_prompt = self._build_enhanced_prompt(base_context)
            base_context['enhanced_prompt'] = enhanced_prompt

            # Кэширование результата
            cache_key = f"enhanced_context_{session_id}"
            cache.set(cache_key, base_context, timeout=self.CONTEXT_TIMEOUT)

            logger.info(f"✅ Enhanced context generated for session {session_id}")
            return base_context

        except Exception as e:
            logger.error(f"❌ Error generating enhanced context: {e}")
            return {'error': str(e), 'fallback_context': self._get_fallback_context()}

    def _get_base_session_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Получение базового контекста сессии"""
        try:
            session = ChatSession.objects.select_related('user').prefetch_related(
                'messages'
            ).get(id=session_id)

            messages = list(session.messages.all().order_by('created_at'))
            recent_messages = messages[-self.MAX_CONTEXT_ITEMS:]

            context = {
                'session_id': str(session.id),
                'user': self._get_user_profile(session.user) if session.user else None,
                'created_at': session.created_at.isoformat(),
                'updated_at': session.updated_at.isoformat(),
                'is_active': session.is_active,
                'message_count': len(messages),
                'recent_messages': [
                    {
                        'role': msg.role,
                        'content': msg.content[:500],  # Ограничение длины
                        'created_at': msg.created_at.isoformat(),
                        'tokens': getattr(msg, 'token_count', 0)
                    }
                    for msg in recent_messages
                ]
            }

            # Извлечение AI контента (временно отключено)
            # TODO: Реализовать связь между ChatMessage и AIContext
            context['ai_contexts'] = {}
            return context

        except ChatSession.DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"❌ Error getting base session context: {e}")
            return None

    def _get_user_profile(self, user: User) -> Dict[str, Any]:
        """Получение профиля пользователя с аналитикой"""
        if not user:
            return None

        cache_key = f"user_profile_{user.id}"
        cached_profile = cache.get(cache_key)

        if cached_profile:
            return cached_profile

        try:
            # Базовая информация
            profile = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': getattr(user, 'phone', None),
                'is_verified': getattr(user, 'is_verified', False),
                'date_joined': user.date_joined.isoformat() if user.date_joined else None,
                'last_login': user.last_login.isoformat() if user.last_login else None
            }

            # Аналитика по клубам
            from clubs.models import Club
            user_clubs = Club.objects.filter(Q(managers=user) | Q(members=user)).distinct()

            profile['clubs_analytics'] = {
                'managed_count': user_clubs.filter(managers=user).count(),
                'member_count': user_clubs.filter(members=user).count(),
                'total_clubs': user_clubs.count(),
                'categories': list(user_clubs.values_list('category__name', flat=True).distinct())
            }

            # Аналитика по чатам
            chat_sessions = ChatSession.objects.filter(user=user)
            profile['chat_analytics'] = {
                'total_sessions': chat_sessions.count(),
                'total_messages': ChatMessage.objects.filter(session__in=chat_sessions).count(),
                'avg_session_length': self._calculate_avg_session_length(chat_sessions),
                'most_active_hour': self._get_most_active_hour(user),
                'preferred_topics': self._get_preferred_topics(user)
            }

            # Поведенческие паттерны
            profile['behavior_patterns'] = self._analyze_behavior_patterns(user)

            # Сохранение в кэш
            cache.set(cache_key, profile, timeout=1800)  # 30 минут

            return profile

        except Exception as e:
            logger.error(f"❌ Error getting user profile: {e}")
            return {'id': user.id, 'error': str(e)}

    def _get_rag_context(self, query: str, base_context: Dict[str, Any]) -> Dict[str, Any]:
        """Получение RAG контекста"""
        try:
            # Формирование обогащенного запроса
            enriched_query = self._enrich_query_with_context(query, base_context)

            # Получение контекста из RAG
            rag_context = self.rag_service.get_enhanced_context(
                query=enriched_query,
                user_context={
                    'user_profile': base_context.get('user'),
                    'message_history': base_context.get('recent_messages', []),
                    'session_metadata': {
                        'message_count': base_context.get('message_count', 0),
                        'session_duration': self._calculate_session_duration(base_context)
                    }
                }
            )

            # Фильтрация и ранжирование результатов
            filtered_context = self._filter_rag_results(rag_context, base_context)

            # Дополнительная постобработка
            enhanced_rag = self._post_process_rag_results(filtered_context, base_context)

            return enhanced_rag

        except Exception as e:
            logger.error(f"❌ Error getting RAG context: {e}")
            return {'error': str(e), 'retrieved_info': {}}

    def _get_predictions(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Получение предиктивной аналитики"""
        try:
            predictions = {}

            # Предсказание следующего вопроса пользователя
            next_question = self.predictive_engine.predict_next_question(context)
            predictions['next_question'] = next_question

            # Предсказание вероятности успеха консультации
            success_probability = self.predictive_engine.predict_success_probability(context)
            predictions['success_probability'] = success_probability

            # Рекомендуемые действия
            recommended_actions = self.predictive_engine.recommend_actions(context)
            predictions['recommended_actions'] = recommended_actions

            # Оценка удовлетворенности
            satisfaction_score = self.predictive_engine.predict_satisfaction(context)
            predictions['satisfaction_score'] = satisfaction_score

            # Время до следующего обращения
            next_interaction = self.predictive_engine.predict_next_interaction(context)
            predictions['next_interaction_prediction'] = next_interaction

            return predictions

        except Exception as e:
            logger.error(f"❌ Error getting predictions: {e}")
            return {}

    def _get_personalization(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Персонализация на основе истории и профиля"""
        try:
            personalization = {
                'tone_adjustments': {},
                'content_preferences': {},
                'communication_style': {},
                'topic_priorities': {}
            }

            user_profile = context.get('user')
            if not user_profile:
                return personalization

            # Анализ тона общения
            chat_analytics = user_profile.get('chat_analytics', {})
            preferred_topics = chat_analytics.get('preferred_topics', {})

            # Настройка тона на предпочтений
            if 'technical' in preferred_topics:
                personalization['tone_adjustments']['formality'] = 'professional'
                personalization['tone_adjustments']['technical_level'] = 'high'
            elif 'general' in preferred_topics:
                personalization['tone_adjustments']['formality'] = 'friendly'
                personalization['tone_adjustments']['technical_level'] = 'medium'

            # Предпочтения по контенту
            clubs_analytics = user_profile.get('clubs_analytics', {})
            if clubs_analytics.get('managed_count', 0) > 0:
                personalization['content_preferences']['club_management'] = True
                personalization['content_preferences']['leadership_tips'] = True

            # Стиль коммуникации
            most_active_hour = chat_analytics.get('most_active_hour')
            if most_active_hour:
                if 9 <= most_active_hour <= 17:
                    personalization['communication_style']['time_preference'] = 'business_hours'
                else:
                    personalization['communication_style']['time_preference'] = 'flexible'

            return personalization

        except Exception as e:
            logger.error(f"❌ Error getting personalization: {e}")
            return {}

    def _analyze_intent(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ интента и извлечение сущностей"""
        try:
            intent_analysis = {
                'primary_intent': None,
                'confidence': 0.0,
                'entities': [],
                'sentiment': 'neutral',
                'urgency': 'normal',
                'complexity': 'medium'
            }

            # Анализ текущего сообщения
            current_message = context.get('current_message', {})
            if current_message:
                intent_analysis.update({
                    'primary_intent': current_message.get('intent'),
                    'confidence': current_message.get('confidence', 0.0),
                    'entities': current_message.get('entities', []),
                    'sentiment': current_message.get('sentiment', 'neutral')
                })

            # Анализ контекста диалога
            recent_messages = context.get('recent_messages', [])
            if recent_messages:
                # Определение срочности
                urgency_patterns = [
                    r'срочно', r'помогите', r'проблема', r'ошибка', r'не работает',
                    r'urgent', r'help', r'asap', r'immediately'
                ]

                last_user_message = None
                for msg in reversed(recent_messages):
                    if msg.get('role') == 'user':
                        last_user_message = msg.get('content', '')
                        break

                if last_user_message:
                    urgency_matches = sum(1 for pattern in urgency_patterns
                                        if re.search(pattern, last_user_message, re.IGNORECASE))

                    if urgency_matches >= 2:
                        intent_analysis['urgency'] = 'high'
                    elif urgency_matches >= 1:
                        intent_analysis['urgency'] = 'medium'

                # Определение сложности
                avg_message_length = sum(len(msg.get('content', '')) for msg in recent_messages[-5:]) / min(5, len(recent_messages))
                if avg_message_length > 200:
                    intent_analysis['complexity'] = 'high'
                elif avg_message_length < 50:
                    intent_analysis['complexity'] = 'low'

            return intent_analysis

        except Exception as e:
            logger.error(f"❌ Error analyzing intent: {e}")
            return {'primary_intent': 'general', 'confidence': 0.5}

    def _build_enhanced_prompt(self, context: Dict[str, Any]) -> str:
        """Построение улучшенного промпта с учетом всего контекста"""
        try:
            prompt_parts = []

            # Системный промпт
            system_prompt = self._get_system_prompt(context)
            prompt_parts.append(system_prompt)

            # Персонализация
            personalization = context.get('personalization', {})
            if personalization:
                personalization_prompt = self._build_personalization_prompt(personalization)
                prompt_parts.append(personalization_prompt)

            # RAG контекст
            rag_context = context.get('rag_context', {})
            if rag_context.get('retrieved_info'):
                rag_prompt = self.rag_service.format_context_for_prompt(rag_context)
                prompt_parts.append(rag_prompt)

            # Предиктивная аналитика
            predictions = context.get('predictions', {})
            if predictions:
                predictions_prompt = self._build_predictions_prompt(predictions)
                prompt_parts.append(predictions_prompt)

            # История диалога
            recent_messages = context.get('recent_messages', [])
            if recent_messages:
                history_prompt = self._build_history_prompt(recent_messages)
                prompt_parts.append(history_prompt)

            # Текущий запрос
            current_message_analysis = context.get('current_message', {})
            if current_message_analysis:
                current_prompt = f"""
🎯 **Текущий запрос пользователя:**
Текст: {current_message_analysis.get('original_text', '')}
Интент: {current_message_analysis.get('intent', 'unknown')}
Уверенность: {current_message_analysis.get('confidence', 0.0):.2f}
Сущности: {current_message_analysis.get('entities', [])}
"""
                prompt_parts.append(current_prompt)

            # Инструкции по ответу
            instructions_prompt = self._build_instructions_prompt(context)
            prompt_parts.append(instructions_prompt)

            # Сборка итогового промпта
            enhanced_prompt = '\n\n'.join(filter(None, prompt_parts))

            return enhanced_prompt

        except Exception as e:
            logger.error(f"❌ Error building enhanced prompt: {e}")
            return self._get_fallback_prompt()

    # Вспомогательные методы
    def _enrich_query_with_context(self, query: str, context: Dict[str, Any]) -> str:
        """Обогащение запроса контекстом"""
        enriched_parts = [query]

        user_profile = context.get('user')
        if user_profile:
            clubs_analytics = user_profile.get('clubs_analytics', {})
            if clubs_analytics.get('managed_count', 0) > 0:
                enriched_parts.append("клубный менеджмент администратор")

            categories = clubs_analytics.get('categories', [])
            if categories:
                enriched_parts.append(f"категории: {', '.join(categories)}")

        return ' '.join(enriched_parts)

    def _filter_rag_results(self, rag_context: Dict[str, Any], base_context: Dict[str, Any]) -> Dict[str, Any]:
        """Фильтрация RAG результатов"""
        threshold = self.CONFIDENCE_THRESHOLD
        filtered_info = {}

        for collection, docs in rag_context.get('retrieved_info', {}).items():
            filtered_docs = [
                doc for doc in docs
                if (1.0 - doc.get('distance', 1.0)) >= threshold
            ]
            if filtered_docs:
                filtered_info[collection] = filtered_docs

        rag_context['retrieved_info'] = filtered_info
        return rag_context

    def _get_fallback_context(self) -> Dict[str, Any]:
        """Запасной контекст при ошибках"""
        return {
            'session_id': 'fallback',
            'user': None,
            'message_count': 0,
            'recent_messages': [],
            'rag_context': {'retrieved_info': {}},
            'predictions': {},
            'personalization': {},
            'intent_analysis': {'primary_intent': 'general'}
        }

    def _get_system_prompt(self, context: Dict[str, Any]) -> str:
        """Получение системного промпта"""
        base_prompt = """
Ты - ИИ-консультант платформы UnitySphere, эксперт по клубам и мероприятиям.
Твоя цель - предоставлять точную, полезную и персонализированную помощь пользователям.
"""
        # Дополнительные инструкции на основе контекста
        intent_analysis = context.get('intent_analysis', {})
        if intent_analysis.get('urgency') == 'high':
            base_prompt += "\nПользователю нужна срочная помощь. Будь максимально оперативным."

        return base_prompt

    def _get_fallback_prompt(self) -> str:
        """Запасной промпт при ошибках"""
        return """
Ты - дружелюбный ИИ-консультант UnitySphere.
Помоги пользователю с его вопросом о платформе.
Если у тебя нет конкретной информации, предложи связаться с поддержкой.
"""

    # Дополнительные методы для построения промптов...
    def _build_personalization_prompt(self, personalization: Dict[str, Any]) -> str:
        return ""  # Реализация

    def _build_predictions_prompt(self, predictions: Dict[str, Any]) -> str:
        return ""  # Реализация

    def _build_history_prompt(self, messages: List[Dict[str, Any]]) -> str:
        return ""  # Реализация

    def _build_instructions_prompt(self, context: Dict[str, Any]) -> str:
        return ""  # Реализация

    def _calculate_avg_session_length(self, sessions) -> float:
        """Расчет средней длины сессии"""
        try:
            durations = []
            for session in sessions:
                if session.created_at and session.updated_at:
                    duration = (session.updated_at - session.created_at).total_seconds()
                    durations.append(duration)

            return sum(durations) / len(durations) if durations else 0.0
        except:
            return 0.0

    def _get_most_active_hour(self, user: User) -> Optional[int]:
        """Определение наиболее активного часа пользователя"""
        try:
            from django.db.models import ExtractHour
            messages = ChatMessage.objects.filter(
                session__user=user,
                role='user'
            ).annotate(
                hour=ExtractHour('created_at')
            ).values('hour').annotate(count=Count('id')).order_by('-count').first()

            return messages['hour'] if messages else None
        except:
            return None

    def _get_preferred_topics(self, user: User) -> Dict[str, int]:
        """Определение предпочитаемых тем"""
        try:
            # Базовая реализация - можно улучшить с помощью NLP
            return {'general': 1, 'clubs': 1}
        except:
            return {}

    def _analyze_behavior_patterns(self, user: User) -> Dict[str, Any]:
        """Анализ поведенческих паттернов"""
        return {
            'activity_level': 'medium',
            'preferred_interaction_time': 'business_hours',
            'response_time_preference': 'normal'
        }

    def _calculate_session_duration(self, context: Dict[str, Any]) -> float:
        """Расчет продолжительности сессии"""
        try:
            created_at = context.get('created_at')
            if created_at:
                created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                now = timezone.now()
                return (now - created).total_seconds()
            return 0.0
        except:
            return 0.0

    def _post_process_rag_results(self, rag_context: Dict[str, Any], base_context: Dict[str, Any]) -> Dict[str, Any]:
        """Постобработка RAG результатов"""
        # Дополнительная обработка результатов
        return rag_context


# Глобальный экземпляр
enhanced_context_service = None


def get_enhanced_context_service():
    """Получение экземпляра улучшенного контекст сервиса"""
    global enhanced_context_service
    if enhanced_context_service is None:
        enhanced_context_service = EnhancedContextService()
    return enhanced_context_service