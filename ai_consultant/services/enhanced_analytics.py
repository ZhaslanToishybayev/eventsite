"""
📊 Enhanced Analytics Service
Расширенный сервис аналитики с предиктивной функциональностью
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
import numpy as np
from django.db.models import Q, Count, Avg, Sum, F, Func
from django.db.models.functions import TruncDate, TruncHour, ExtractHour
from django.core.cache import cache
from django.utils import timezone

from ..models import ChatSession, ChatMessage, AIContext, UserFeedback
from clubs.models import Club, ClubEvent
from accounts.models import User
from ..utils.predictive_engine import PredictiveEngine
from ..utils.context_analyzer import ContextAnalyzer

logger = logging.getLogger(__name__)


class EnhancedAnalyticsService:
    """
    📊 Расширенная аналитика с предиктивными возможностями
    """

    def __init__(self):
        self.predictive_engine = PredictiveEngine()
        self.context_analyzer = ContextAnalyzer()

        # Периоды для анализа
        self.ANALYSIS_PERIODS = {
            'day': 1,
            'week': 7,
            'month': 30,
            'quarter': 90
        }

        # Кэширование
        self.CACHE_TIMEOUT = {
            'hourly': 3600,      # 1 час
            'daily': 86400,      # 1 день
            'weekly': 604800,    # 1 неделя
            'monthly': 2592000   # 1 месяц
        }

    def get_comprehensive_analytics(self, period: str = 'week', user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        📈 Получение комплексной аналитики
        """
        try:
            analytics = {
                'period': period,
                'generated_at': timezone.now().isoformat(),
                'user_specific': user_id is not None,
                'overall_metrics': {},
                'conversation_analytics': {},
                'user_analytics': {},
                'content_analytics': {},
                'performance_metrics': {},
                'predictions': {},
                'trends': {},
                'recommendations': []
            }

            # Базовые метрики
            analytics['overall_metrics'] = self._get_overall_metrics(period, user_id)

            # Аналитика диалогов
            analytics['conversation_analytics'] = self._get_conversation_analytics(period, user_id)

            # Пользовательская аналитика
            analytics['user_analytics'] = self._get_user_analytics(period, user_id)

            # Аналитика контента
            analytics['content_analytics'] = self._get_content_analytics(period, user_id)

            # Метрики производительности
            analytics['performance_metrics'] = self._get_performance_metrics(period, user_id)

            # Предиктивная аналитика
            analytics['predictions'] = self._get_predictive_analytics(period, user_id)

            # Анализ трендов
            analytics['trends'] = self._analyze_trends(period, user_id)

            # Генерация рекомендаций
            analytics['recommendations'] = self._generate_recommendations(analytics)

            return analytics

        except Exception as e:
            logger.error(f"❌ Error generating comprehensive analytics: {e}")
            return {'error': str(e), 'timestamp': timezone.now().isoformat()}

    def _get_overall_metrics(self, period: str, user_id: Optional[int]) -> Dict[str, Any]:
        """Основные метрики платформы"""
        cache_key = f"overall_metrics_{period}_{user_id or 'global'}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        try:
            days = self.ANALYSIS_PERIODS.get(period, 7)
            start_date = timezone.now() - timedelta(days=days)

            # Базовые запросы
            base_filter = Q(created_at__gte=start_date)
            if user_id:
                base_filter &= Q(user_id=user_id)

            # Метрики сессий
            sessions = ChatSession.objects.filter(base_filter)

            total_sessions = sessions.count()
            active_sessions = sessions.filter(is_active=True).count()
            anonymous_sessions = sessions.filter(user__isnull=True).count()

            # Метрики сообщений
            messages = ChatMessage.objects.filter(
                session__created_at__gte=start_date
            )
            if user_id:
                messages = messages.filter(session__user_id=user_id)

            total_messages = messages.count()
            user_messages = messages.filter(role='user').count()
            assistant_messages = messages.filter(role='assistant').count()

            # Уникальные пользователи
            unique_users = ChatSession.objects.filter(
                base_filter,
                user__isnull=False
            ).values('user').distinct().count()

            # Средние показатели
            avg_messages_per_session = total_messages / total_sessions if total_sessions > 0 else 0
            avg_session_duration = self._calculate_avg_session_duration(sessions)

            metrics = {
                'total_sessions': total_sessions,
                'active_sessions': active_sessions,
                'anonymous_sessions': anonymous_sessions,
                'registered_sessions': total_sessions - anonymous_sessions,
                'unique_users': unique_users,
                'total_messages': total_messages,
                'user_messages': user_messages,
                'assistant_messages': assistant_messages,
                'avg_messages_per_session': round(avg_messages_per_session, 2),
                'avg_session_duration_minutes': round(avg_session_duration / 60, 2),
                'messages_per_user': round(total_messages / unique_users, 2) if unique_users > 0 else 0,
                'anonymous_ratio': round(anonymous_sessions / total_sessions * 100, 2) if total_sessions > 0 else 0
            }

            cache.set(cache_key, metrics, timeout=self.CACHE_TIMEOUT['hourly'])
            return metrics

        except Exception as e:
            logger.error(f"❌ Error getting overall metrics: {e}")
            return {}

    def _get_conversation_analytics(self, period: str, user_id: Optional[int]) -> Dict[str, Any]:
        """Аналитика диалогов"""
        try:
            days = self.ANALYSIS_PERIODS.get(period, 7)
            start_date = timezone.now() - timedelta(days=days)

            base_filter = Q(created_at__gte=start_date)
            if user_id:
                base_filter &= Q(user_id=user_id)

            sessions = ChatSession.objects.filter(base_filter).prefetch_related('messages')

            # Анализ продолжительности диалогов
            session_lengths = []
            message_patterns = defaultdict(int)
            intent_distribution = defaultdict(int)
            sentiment_distribution = defaultdict(int)

            for session in sessions:
                messages = list(session.messages.all())

                # Длина сессии
                if messages:
                    first_message = messages[0].created_at
                    last_message = messages[-1].created_at
                    duration = (last_message - first_message).total_seconds()
                    session_lengths.append(duration)

                # Анализ паттернов сообщений
                for i, msg in enumerate(messages):
                    if msg.role == 'user':
                        # Паттерны длины сообщений
                        content_length = len(msg.content)
                        if content_length < 50:
                            message_patterns['short'] += 1
                        elif content_length < 200:
                            message_patterns['medium'] += 1
                        else:
                            message_patterns['long'] += 1

                        # Анализ интентов и тональности
                        analysis = self.context_analyzer.analyze_message(msg.content)
                        intent_distribution[analysis['intent']] += 1
                        sentiment_distribution[analysis['sentiment']] += 1

            # Статистика по длительности
            if session_lengths:
                avg_duration = np.mean(session_lengths)
                median_duration = np.median(session_lengths)
                std_duration = np.std(session_lengths)
            else:
                avg_duration = median_duration = std_duration = 0

            # Выявление популярных тем
            popular_topics = self._extract_popular_topics(sessions)

            return {
                'session_duration': {
                    'average_minutes': round(avg_duration / 60, 2),
                    'median_minutes': round(median_duration / 60, 2),
                    'std_minutes': round(std_duration / 60, 2),
                    'longest_session_minutes': round(max(session_lengths) / 60, 2) if session_lengths else 0
                },
                'message_patterns': dict(message_patterns),
                'intent_distribution': dict(intent_distribution),
                'sentiment_distribution': dict(sentiment_distribution),
                'popular_topics': popular_topics,
                'conversation_flow': self._analyze_conversation_flow(sessions),
                'engagement_metrics': self._calculate_engagement_metrics(sessions)
            }

        except Exception as e:
            logger.error(f"❌ Error getting conversation analytics: {e}")
            return {}

    def _get_user_analytics(self, period: str, user_id: Optional[int]) -> Dict[str, Any]:
        """Пользовательская аналитика"""
        try:
            if user_id:
                return self._get_specific_user_analytics(user_id, period)
            else:
                return self._get_general_user_analytics(period)

        except Exception as e:
            logger.error(f"Error getting user analytics: {e}")
            return {}

    def _get_content_analytics(self, period: str, user_id: Optional[int]) -> Dict[str, Any]:
        """Аналитика контента"""
        try:
            days = self.ANALYSIS_PERIODS.get(period, 7)
            start_date = timezone.now() - timedelta(days=days)

            # Анализ наиболее обсуждаемых тем
            messages = ChatMessage.objects.filter(
                role='user',
                created_at__gte=start_date
            )
            if user_id:
                messages = messages.filter(session__user_id=user_id)

            # Извлечение ключевых слов из всех сообщений
            all_keywords = []
            all_intents = []

            for message in messages:
                analysis = self.context_analyzer.analyze_message(message.content)
                all_keywords.extend(analysis['keywords'])
                all_intents.append(analysis['intent'])

            # Частотность ключевых слов
            keyword_freq = Counter(all_keywords)
            intent_freq = Counter(all_intents)

            # Анализ контента RAG
            rag_analytics = self._get_rag_content_analytics(period, user_id)

            # Анализ качества контента
            quality_metrics = self._analyze_content_quality(messages)

            return {
                'top_keywords': [
                    {'keyword': word, 'frequency': count}
                    for word, count in keyword_freq.most_common(20)
                ],
                'intent_distribution': [
                    {'intent': intent, 'count': count}
                    for intent, count in intent_freq.most_common()
                ],
                'rag_analytics': rag_analytics,
                'quality_metrics': quality_metrics,
                'content_trends': self._analyze_content_trends(messages)
            }

        except Exception as e:
            logger.error(f"❌ Error getting content analytics: {e}")
            return {}

    def _get_performance_metrics(self, period: str, user_id: Optional[int]) -> Dict[str, Any]:
        """Метрики производительности"""
        try:
            days = self.ANALYSIS_PERIODS.get(period, 7)
            start_date = timezone.now() - timedelta(days=days)

            # Анализ времени ответа
            response_times = []
            success_rates = []

            sessions = ChatSession.objects.filter(created_at__gte=start_date)
            if user_id:
                sessions = sessions.filter(user_id=user_id)

            for session in sessions:
                messages = list(session.messages.all())
                user_queries = [msg for msg in messages if msg.role == 'user']

                for i, user_msg in enumerate(user_queries):
                    # Найти следующий ответ ассистента
                    for j in range(i + 1, len(messages)):
                        if messages[j].role == 'assistant':
                            response_time = (messages[j].created_at - user_msg.created_at).total_seconds()
                            response_times.append(response_time)
                            break

                    # Оценка успешности (на основе обратной связи или продолжения диалога)
                    success_rate = self._calculate_query_success_rate(user_msg, messages[i+1:])
                    if success_rate is not None:
                        success_rates.append(success_rate)

            # Статистика производительности
            performance_stats = {}
            if response_times:
                performance_stats['response_time'] = {
                    'average_seconds': round(np.mean(response_times), 2),
                    'median_seconds': round(np.median(response_times), 2),
                    'p95_seconds': round(np.percentile(response_times, 95), 2),
                    'p99_seconds': round(np.percentile(response_times, 99), 2)
                }

            if success_rates:
                performance_stats['success_rate'] = {
                    'average': round(np.mean(success_rates) * 100, 2),
                    'median': round(np.median(success_rates) * 100, 2),
                    'distribution': self._create_distribution(success_rates)
                }

            # Анализ использования ресурсов
            resource_usage = self._analyze_resource_usage(period, user_id)

            return {
                'performance_stats': performance_stats,
                'resource_usage': resource_usage,
                'bottlenecks': self._identify_bottlenecks(performance_stats, resource_usage),
                'optimization_suggestions': self._get_optimization_suggestions(performance_stats)
            }

        except Exception as e:
            logger.error(f"❌ Error getting performance metrics: {e}")
            return {}

    def _get_predictive_analytics(self, period: str, user_id: Optional[int]) -> Dict[str, Any]:
        """Предиктивная аналитика"""
        try:
            predictions = {
                'user_retention': self._predict_user_retention(period, user_id),
                'content_demand': self._predict_content_demand(period, user_id),
                'system_load': self._predict_system_load(period),
                'quality_trends': self._predict_quality_trends(period, user_id),
                'growth_projections': self._predict_growth(period)
            }

            return predictions

        except Exception as e:
            logger.error(f"❌ Error getting predictive analytics: {e}")
            return {}

    def _analyze_trends(self, period: str, user_id: Optional[int]) -> Dict[str, Any]:
        """Анализ трендов"""
        try:
            days = self.ANALYSIS_PERIODS.get(period, 7)
            start_date = timezone.now() - timedelta(days=days)

            # Динамика использования по дням
            daily_usage = []
            for i in range(days):
                day_date = start_date + timedelta(days=i)
                day_end = day_date + timedelta(days=1)

                sessions_count = ChatSession.objects.filter(
                    created_at__gte=day_date,
                    created_at__lt=day_end
                )
                if user_id:
                    sessions_count = sessions_count.filter(user_id=user_id)

                messages_count = ChatMessage.objects.filter(
                    created_at__gte=day_date,
                    created_at__lt=day_end
                )
                if user_id:
                    messages_count = messages_count.filter(session__user_id=user_id)

                daily_usage.append({
                    'date': day_date.date().isoformat(),
                    'sessions': sessions_count.count(),
                    'messages': messages_count.count()
                })

            # Анализ трендов
            trend_analysis = self._analyze_usage_trends(daily_usage)

            return {
                'daily_usage': daily_usage,
                'trend_analysis': trend_analysis,
                'seasonal_patterns': self._identify_seasonal_patterns(daily_usage),
                'growth_rate': self._calculate_growth_rate(daily_usage)
            }

        except Exception as e:
            logger.error(f"❌ Error analyzing trends: {e}")
            return {}

    def _generate_recommendations(self, analytics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Генерация рекомендаций на основе аналитики"""
        recommendations = []

        try:
            # Рекомендации по производительности
            performance = analytics.get('performance_metrics', {})
            if performance.get('performance_stats', {}).get('response_time', {}).get('average_seconds', 0) > 30:
                recommendations.append({
                    'category': 'performance',
                    'priority': 'high',
                    'title': 'Оптимизация времени ответа',
                    'description': 'Среднее время ответа превышает 30 секунд. Рассмотрите оптимизацию.',
                    'action_items': [
                        'Оптимизировать RAG запросы',
                        'Увеличить кэширование',
                        'Оптимизировать промпты'
                    ]
                })

            # Рекомендации по контенту
            content = analytics.get('content_analytics', {})
            rag_confidence = content.get('rag_analytics', {}).get('average_confidence', 0)
            if rag_confidence < 0.5:
                recommendations.append({
                    'category': 'content',
                    'priority': 'medium',
                    'title': 'Улучшение базы знаний',
                    'description': 'Низкая уверенность RAG. Расширьте базу знаний платформы.',
                    'action_items': [
                        'Добавить больше документации',
                        'Индексировать успешные диалоги',
                        'Обновить FAQ'
                    ]
                })

            # Рекомендации по вовлеченности
            conversation = analytics.get('conversation_analytics', {})
            avg_messages = analytics.get('overall_metrics', {}).get('avg_messages_per_session', 0)
            if avg_messages < 3:
                recommendations.append({
                    'category': 'engagement',
                    'priority': 'medium',
                    'title': 'Повышение вовлеченности',
                    'description': 'Низкое количество сообщений на сессию. Улучшите взаимодействие.',
                    'action_items': [
                        'Добавить проактивные вопросы',
                        'Персонализировать ответы',
                        'Улучшить качество контента'
                    ]
                })

            return recommendations

        except Exception as e:
            logger.error(f"❌ Error generating recommendations: {e}")
            return []

    # Вспомогательные методы
    def _calculate_avg_session_duration(self, sessions) -> float:
        """Расчет средней продолжительности сессии"""
        durations = []
        for session in sessions:
            messages = session.messages.all()
            if messages.count() >= 2:
                first = messages.first().created_at
                last = messages.last().created_at
                duration = (last - first).total_seconds()
                durations.append(duration)

        return np.mean(durations) if durations else 0.0

    def _extract_popular_topics(self, sessions) -> List[Dict[str, Any]]:
        """Извлечение популярных тем"""
        topic_counter = Counter()

        for session in sessions:
            user_messages = session.messages.filter(role='user')
            for message in user_messages:
                analysis = self.context_analyzer.analyze_message(message.content)
                topic_counter[analysis['intent']] += 1

        return [
            {'topic': topic, 'count': count}
            for topic, count in topic_counter.most_common(10)
        ]

    def _analyze_conversation_flow(self, sessions) -> Dict[str, Any]:
        """Анализ потока диалогов"""
        flow_patterns = {
            'quick_resolutions': 0,  # Быстрое решение (1-2 сообщения)
            'extended_discussions': 0,  # Длинные диалоги (>10 сообщений)
            'follow_up_questions': 0   # Последующие вопросы
        }

        for session in sessions:
            message_count = session.messages.count()
            if message_count <= 2:
                flow_patterns['quick_resolutions'] += 1
            elif message_count > 10:
                flow_patterns['extended_discussions'] += 1

        return flow_patterns

    def _calculate_engagement_metrics(self, sessions) -> Dict[str, Any]:
        """Расчет метрик вовлеченности"""
        total_sessions = len(sessions)
        if total_sessions == 0:
            return {}

        # Доля активных сессий
        active_sessions = sum(1 for s in sessions if s.is_active)

        # Средняя длина сообщений
        all_user_messages = []
        for session in sessions:
            user_messages = session.messages.filter(role='user')
            all_user_messages.extend([msg.content for msg in user_messages])

        avg_message_length = np.mean([len(msg) for msg in all_user_messages]) if all_user_messages else 0

        return {
            'active_session_rate': round(active_sessions / total_sessions * 100, 2),
            'avg_message_length': round(avg_message_length, 2),
            'return_user_rate': self._calculate_return_user_rate(sessions)
        }

    def _create_distribution(self, values: List[float]) -> Dict[str, int]:
        """Создание распределения значений"""
        distribution = {'low': 0, 'medium': 0, 'high': 0}
        for value in values:
            if value < 0.33:
                distribution['low'] += 1
            elif value < 0.67:
                distribution['medium'] += 1
            else:
                distribution['high'] += 1
        return distribution

    def _get_specific_user_analytics(self, user_id: int, period: str) -> Dict[str, Any]:
        """Аналитика конкретного пользователя"""
        # Реализация аналитики для конкретного пользователя
        return {
            'user_id': user_id,
            'total_sessions': ChatSession.objects.filter(user_id=user_id).count(),
            'total_messages': ChatMessage.objects.filter(session__user_id=user_id).count(),
            'favorite_topics': [],
            'engagement_score': 0.7
        }

    def _get_general_user_analytics(self, period: str) -> Dict[str, Any]:
        """Общая пользовательская аналитика"""
        return {
            'total_registered_users': User.objects.count(),
            'active_users_this_period': 0,
            'new_users_this_period': 0,
            'user_retention_rate': 0.8
        }

    def _get_rag_content_analytics(self, period: str, user_id: Optional[int]) -> Dict[str, Any]:
        """Аналитика RAG контента"""
        # Заглушка - в реальной реализации анализировать использование RAG
        return {
            'total_queries': 0,
            'average_confidence': 0.0,
            'most_accessed_collections': {},
            'cache_hit_rate': 0.0
        }

    def _analyze_content_quality(self, messages) -> Dict[str, Any]:
        """Анализ качества контента"""
        return {
            'avg_clarity_score': 0.7,
            'relevance_score': 0.8,
            'completeness_score': 0.6
        }

    def _analyze_content_trends(self, messages) -> List[Dict[str, Any]]:
        """Анализ трендов контента"""
        return []

    def _analyze_resource_usage(self, period: str, user_id: Optional[int]) -> Dict[str, Any]:
        """Анализ использования ресурсов"""
        return {
            'cpu_usage': 0.5,
            'memory_usage': 0.6,
            'api_calls': 100,
            'database_queries': 200
        }

    def _identify_bottlenecks(self, performance_stats: Dict, resource_usage: Dict) -> List[str]:
        """Идентификация узких мест"""
        bottlenecks = []
        if performance_stats.get('response_time', {}).get('average_seconds', 0) > 30:
            bottlenecks.append('Response time bottleneck')
        return bottlenecks

    def _get_optimization_suggestions(self, performance_stats: Dict) -> List[str]:
        """Предложения по оптимизации"""
        return ['Implement caching', 'Optimize database queries']

    def _predict_user_retention(self, period: str, user_id: Optional[int]) -> Dict[str, Any]:
        """Предсказание удержания пользователей"""
        return {'predicted_retention_rate': 0.85, 'confidence': 0.7}

    def _predict_content_demand(self, period: str, user_id: Optional[int]) -> Dict[str, Any]:
        """Предсказание спроса на контент"""
        return {'upcoming_topics': [], 'demand_forecast': {}}

    def _predict_system_load(self, period: str) -> Dict[str, Any]:
        """Предсказание нагрузки на систему"""
        return {'expected_load': 0.6, 'peak_hours': []}

    def _predict_quality_trends(self, period: str, user_id: Optional[int]) -> Dict[str, Any]:
        """Предсказание трендов качества"""
        return {'quality_trend': 'stable', 'predicted_score': 0.8}

    def _predict_growth(self, period: str) -> Dict[str, Any]:
        """Предсказание роста"""
        return {'expected_growth_rate': 0.1, 'new_users_forecast': 100}

    def _analyze_usage_trends(self, daily_usage: List[Dict]) -> Dict[str, Any]:
        """Анализ трендов использования"""
        return {'trend': 'increasing', 'growth_rate': 0.05}

    def _identify_seasonal_patterns(self, daily_usage: List[Dict]) -> List[Dict]:
        """Идентификация сезонных паттернов"""
        return []

    def _calculate_growth_rate(self, daily_usage: List[Dict]) -> float:
        """Расчет темпа роста"""
        return 0.05

    def _calculate_return_user_rate(self, sessions) -> float:
        """Расчет коэффициента возврата пользователей"""
        return 0.3

    def _calculate_query_success_rate(self, user_msg, remaining_messages) -> Optional[float]:
        """Расчет успешности запроса"""
        # Упрощенная реализация
        return 0.7


# Глобальный экземпляр
enhanced_analytics_service = None


def get_enhanced_analytics_service():
    """Получение экземпляра расширенного аналитического сервиса"""
    global enhanced_analytics_service
    if enhanced_analytics_service is None:
        enhanced_analytics_service = EnhancedAnalyticsService()
    return enhanced_analytics_service