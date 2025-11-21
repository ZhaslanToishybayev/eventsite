"""
🔮 Predictive Engine
ML-движок для предиктивной аналитики и рекомендаций
"""

import logging
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
import json
from django.core.cache import cache
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans

logger = logging.getLogger(__name__)


class PredictiveEngine:
    """
    🔮 Предиктивный движок для анализа поведения и прогнозирования
    """

    def __init__(self):
        # Исторические данные для обучения
        self.conversation_patterns = defaultdict(list)
        self.success_patterns = defaultdict(list)
        self.user_behaviors = defaultdict(dict)

        # Пороги и параметры
        self.MIN_SAMPLES_FOR_PREDICTION = 5
        self.SIMILARITY_THRESHOLD = 0.3
        self.SUCCESS_THRESHOLD = 0.7

        # Кэшированные модели
        self._vectorizer = None
        self._topic_model = None
        self._intent_patterns = None

    def predict_next_question(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        🔮 Предсказание следующего вопроса пользователя
        """
        try:
            prediction = {
                'predicted_questions': [],
                'confidence': 0.0,
                'reasoning': '',
                'based_on': []
            }

            # Извлечение релевантных данных из контекста
            recent_messages = context.get('recent_messages', [])
            intent_analysis = context.get('intent_analysis', {})
            current_intent = intent_analysis.get('primary_intent') if intent_analysis else 'general'
            user_profile = context.get('user', {})

            if len(recent_messages) < 2:
                return prediction

            # Анализ последовательности интентов
            intent_sequence = self._extract_intent_sequence(recent_messages)

            # Поиск похожих исторических последовательностей
            similar_patterns = self._find_similar_patterns(intent_sequence)

            if similar_patterns:
                # Предсказание следующего интента на основе паттернов
                next_intents = self._predict_next_intent(similar_patterns)

                # Генерация вопросов на основе предсказанных интентов
                for intent_data in next_intents[:3]:
                    intent = intent_data['intent']
                    confidence = intent_data['confidence']

                    generated_questions = self._generate_questions_for_intent(
                        intent, context, user_profile
                    )

                    for question in generated_questions:
                        prediction['predicted_questions'].append({
                            'question': question,
                            'intent': intent,
                            'confidence': confidence * 0.8,  # Уменьшаем уверенность
                            'category': self._categorize_question(question)
                        })

                # Сортировка по уверенности
                prediction['predicted_questions'].sort(
                    key=lambda x: x['confidence'], reverse=True
                )

                # Общая уверенность
                if prediction['predicted_questions']:
                    prediction['confidence'] = prediction['predicted_questions'][0]['confidence']
                    prediction['reasoning'] = "Based on similar conversation patterns"
                    prediction['based_on'] = [p['pattern'] for p in similar_patterns[:3]]

            return prediction

        except Exception as e:
            logger.error(f"❌ Error predicting next question: {e}")
            return {
                'predicted_questions': [],
                'confidence': 0.0,
                'error': str(e)
            }

    def predict_success_probability(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        📊 Предсказание вероятности успешной консультации
        """
        try:
            # Защита от None context
            if context is None:
                context = {}
            
            success_analysis = {
                'overall_probability': 0.5,
                'factors': {},
                'recommendations': [],
                'risk_level': 'medium'
            }

            # Факторы успеха
            factors = {
                'query_clarity': self._assess_query_clarity(context) or 0.5,
                'rag_confidence': self._assess_rag_confidence(context) or 0.5,
                'user_engagement': self._assess_user_engagement(context) or 0.5,
                'conversation_complexity': self._assess_complexity_factor(context) or 0.5,
                'historical_success_rate': self._get_historical_success_rate(context) or 0.5,
                'availability_of_resources': self._check_resource_availability(context) or 0.5
            }

            success_analysis['factors'] = factors

            # Взвешенная оценка вероятности успеха
            weights = {
                'query_clarity': 0.2,
                'rag_confidence': 0.25,
                'user_engagement': 0.15,
                'conversation_complexity': 0.15,
                'historical_success_rate': 0.15,
                'availability_of_resources': 0.1
            }

            weighted_score = sum(
                factors[factor] * weights[factor]
                for factor in weights
            )

            success_analysis['overall_probability'] = min(max(weighted_score, 0.0), 1.0)

            # Уровень риска
            if success_analysis['overall_probability'] > 0.7:
                success_analysis['risk_level'] = 'low'
            elif success_analysis['overall_probability'] < 0.4:
                success_analysis['risk_level'] = 'high'
            else:
                success_analysis['risk_level'] = 'medium'

            # Рекомендации для улучшения
            success_analysis['recommendations'] = self._generate_success_recommendations(
                factors, success_analysis['overall_probability']
            )

            return success_analysis

        except Exception as e:
            logger.error(f"❌ Error predicting success probability: {e}")
            return {
                'overall_probability': 0.5,
                'factors': {},
                'error': str(e)
            }

    def recommend_actions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        🎯 Рекомендуемые действия для консультанта
        """
        try:
            recommendations = []

            # Анализ текущей ситуации
            intent_analysis = context.get('intent_analysis', {})
            intent = intent_analysis.get('primary_intent') if intent_analysis else 'general'
            urgency = intent_analysis.get('urgency', 'normal') if intent_analysis else 'normal'
            user_profile = context.get('user', {})
            rag_context = context.get('rag_context', {})

            # Рекомендации на основе интента
            if intent == 'club_creation':
                recommendations.extend(self._get_club_creation_recommendations(user_profile, rag_context))
            elif intent == 'technical_help':
                recommendations.extend(self._get_technical_help_recommendations(urgency))
            elif intent == 'recommendation':
                recommendations.extend(self._get_recommendation_actions(user_profile, rag_context))

            # Рекомендации на основе срочности
            if urgency == 'high':
                recommendations.append({
                    'action': 'escalate_priority',
                    'description': 'Срочно ускорить обработку запроса',
                    'priority': 'high',
                    'automation_level': 'manual'
                })

            # Рекомендации на основе профиля пользователя
            if user_profile:
                if user_profile.get('chat_analytics', {}).get('total_sessions', 0) == 1:
                    recommendations.append({
                        'action': 'provide_welcome_guide',
                        'description': 'Предоставить приветственное руководство для новичка',
                        'priority': 'medium',
                        'automation_level': 'automated'
                    })

            # Рекомендации на основе RAG контекста
            rag_confidence = rag_context.get('overall_confidence', 0.0)
            if rag_confidence < 0.3:
                recommendations.append({
                    'action': 'fallback_to_general',
                    'description': 'Использовать общие знания при низкой уверенности RAG',
                    'priority': 'high',
                    'automation_level': 'automated'
                })

            # Ранжирование рекомендаций
            priority_order = {'high': 3, 'medium': 2, 'low': 1}
            recommendations.sort(
                key=lambda x: priority_order.get(x.get('priority', 'low'), 0),
                reverse=True
            )

            return recommendations[:5]  # Топ-5 рекомендаций

        except Exception as e:
            logger.error(f"❌ Error generating recommendations: {e}")
            return []

    def predict_satisfaction(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        😊 Предсказание удовлетворенности пользователя
        """
        try:
            satisfaction = {
                'predicted_score': 3.0,  # 1-5 шкала
                'confidence': 0.5,
                'factors': {},
                'improvement_suggestions': []
            }

            # Факторы удовлетворенности
            factors = {
                'response_relevance': self._assess_response_relevance(context),
                'response_speed': self._assess_response_speed(context),
                'problem_resolution': self._assess_problem_resolution(context),
                'user_sentiment': self._assess_user_sentiment(context),
                'conversation_flow': self._assess_conversation_flow(context)
            }

            satisfaction['factors'] = factors

            # Расчет общей оценки
            weights = {'response_relevance': 0.3, 'response_speed': 0.2,
                      'problem_resolution': 0.3, 'user_sentiment': 0.1, 'conversation_flow': 0.1}

            weighted_score = sum(
                factors[factor] * weights[factor] * 5  # Конвертация в 1-5 шкалу
                for factor in weights
            )

            satisfaction['predicted_score'] = min(max(weighted_score, 1.0), 5.0)
            satisfaction['confidence'] = self._calculate_satisfaction_confidence(factors)

            # Предложения по улучшению
            if satisfaction['predicted_score'] < 3.5:
                satisfaction['improvement_suggestions'] = self._get_improvement_suggestions(factors)

            return satisfaction

        except Exception as e:
            logger.error(f"❌ Error predicting satisfaction: {e}")
            return {
                'predicted_score': 3.0,
                'confidence': 0.3,
                'error': str(e)
            }

    def predict_next_interaction(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        ⏰ Предсказание времени следующего взаимодействия
        """
        try:
            prediction = {
                'estimated_hours': 24.0,
                'confidence': 0.3,
                'factors': {},
                'next_likely_topic': None
            }

            user_profile = context.get('user', {})
            if not user_profile:
                return prediction

            # Исторические паттерны взаимодействия
            user_id = user_profile.get('id')
            if user_id:
                historical_patterns = self._get_user_interaction_patterns(user_id)

                if historical_patterns:
                    avg_hours = np.mean([p['hours_between'] for p in historical_patterns])
                    prediction['estimated_hours'] = avg_hours
                    prediction['confidence'] = min(len(historical_patterns) / 10.0, 1.0)

            # Факторы влияющие на время следующего взаимодействия
            satisfaction_score_dict = (context.get('predictions') or {}).get('satisfaction_score', {})
            factors = {
                'query_resolution': self._assess_query_resolution(context),
                'user_engagement': self._assess_user_engagement_level(context),
                'satisfaction_prediction': satisfaction_score_dict.get('predicted_score', 3.0)
            }

            prediction['factors'] = factors

            # Корректировка времени на основе факторов
            if factors['query_resolution'] > 0.7:  # Хорошее разрешение
                prediction['estimated_hours'] *= 1.5  # Следующий контакт позже
            elif factors['query_resolution'] < 0.3:  # Плохое разрешение
                prediction['estimated_hours'] *= 0.5  # Следующий контакт скорее

            # Предсказание следующей темы
            prediction['next_likely_topic'] = self._predict_next_topic(context)

            return prediction

        except Exception as e:
            logger.error(f"❌ Error predicting next interaction: {e}")
            return {
                'estimated_hours': 24.0,
                'confidence': 0.1,
                'error': str(e)
            }

    # Вспомогательные методы
    def _extract_intent_sequence(self, messages: List[Dict[str, Any]]) -> List[str]:
        """Извлечение последовательности интентов из сообщений"""
        sequence = []
        for msg in messages:
            if msg.get('role') == 'user':
                content = msg.get('content', '')
                # Простая эвристика для определения интента
                if 'создать' in content.lower() and 'клуб' in content.lower():
                    sequence.append('club_creation')
                elif 'вступить' in content.lower() or 'присоединиться' in content.lower():
                    sequence.append('club_joining')
                elif 'мероприятие' in content.lower() or 'событие' in content.lower():
                    sequence.append('event_creation')
                elif 'помощь' in content.lower() or 'проблема' in content.lower():
                    sequence.append('technical_help')
                else:
                    sequence.append('general')
        return sequence

    def _find_similar_patterns(self, current_sequence: List[str]) -> List[Dict[str, Any]]:
        """Поиск похожих паттернов в истории"""
        # Упрощенная реализация
        return [
            {'pattern': current_sequence, 'similarity': 1.0, 'next_intent': 'general'}
        ]

    def _predict_next_intent(self, patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Предсказание следующего интента на основе паттернов"""
        intent_counts = defaultdict(int)
        total_similarity = 0

        for pattern in patterns:
            next_intent = pattern.get('next_intent', 'general')
            similarity = pattern.get('similarity', 1.0)
            intent_counts[next_intent] += similarity
            total_similarity += similarity

        # Конвертация в вероятности
        predictions = []
        for intent, count in intent_counts.items():
            confidence = count / total_similarity if total_similarity > 0 else 0
            predictions.append({
                'intent': intent,
                'confidence': confidence
            })

        return sorted(predictions, key=lambda x: x['confidence'], reverse=True)

    def _generate_questions_for_intent(self, intent: str, context: Dict[str, Any], user_profile: Dict[str, Any]) -> List[str]:
        """Генерация вопросов для предсказанного интента"""
        question_templates = {
            'club_creation': [
                "Какую категорию клуба вы хотите создать?",
                "Есть ли у вас опыт управления клубами?",
                "Сколько человек вы планируете привлечь в клуб?"
            ],
            'club_joining': [
                "Какие клубы вас интересуют?",
                "Готовы ли вы активно участвовать в жизни клуба?",
                "Есть ли у вас специфические интересы?"
            ],
            'event_creation': [
                "Какого типа мероприятие вы планируете?",
                "Когда и где оно состоится?",
                "Сколько участников ожидается?"
            ],
            'technical_help': [
                "С какой именно проблемой вы столкнулись?",
                "Пытались ли вы уже решить эту проблему?",
                "Есть ли сообщения об ошибках?"
            ]
        }

        return question_templates.get(intent, ["Чем еще я могу вам помочь?"])

    def _categorize_question(self, question: str) -> str:
        """Категоризация вопроса"""
        question_lower = question.lower()
        if 'категория' in question_lower or 'тип' in question_lower:
            return 'classification'
        elif 'опыт' in question_lower or 'готовность' in question_lower:
            return 'qualification'
        elif 'когда' in question_lower or 'где' in question_lower:
            return 'logistics'
        else:
            return 'general'

    def _assess_query_clarity(self, context: Dict[str, Any]) -> float:
        """Оценка ясности запроса"""
        if context is None:
            return 0.5
        current_message = context.get('current_message', {})
        if current_message is None:
            current_message = {}
        complexity = current_message.get('complexity', 'medium')

        if complexity == 'low':
            return 0.9
        elif complexity == 'medium':
            return 0.7
        else:
            return 0.5

    def _assess_rag_confidence(self, context: Dict[str, Any]) -> float:
        """Оценка уверенности RAG"""
        if context is None:
            return 0.5
        rag_context = context.get('rag_context')
        if not rag_context or rag_context is None:
            return 0.5
        return rag_context.get('overall_confidence', 0.5)

    def _assess_user_engagement(self, context: Dict[str, Any]) -> float:
        """Оценка вовлеченности пользователя"""
        if context is None:
            return 0.5
        user_profile = context.get('user', {})
        if user_profile is None:
            user_profile = {}
        chat_analytics = user_profile.get('chat_analytics', {})
        engagement = chat_analytics.get('engagement_level', 'medium')

        if engagement == 'high':
            return 0.9
        elif engagement == 'medium':
            return 0.6
        else:
            return 0.3

    def _assess_complexity_factor(self, context: Dict[str, Any]) -> float:
        """Оценка фактора сложности"""
        message_count = context.get('message_count', 0)
        if message_count < 3:
            return 0.9  # Простые диалоги более успешны
        elif message_count < 10:
            return 0.7
        else:
            return 0.5

    def _get_historical_success_rate(self, context: Dict[str, Any]) -> float:
        """Получение исторической оценки успеха"""
        # Упрощенная реализация
        return 0.7

    def _check_resource_availability(self, context: Dict[str, Any]) -> float:
        """Проверка доступности ресурсов"""
        rag_context = context.get('rag_context', {})
        total_docs = rag_context.get('total_docs_found', 0)
        return min(total_docs / 5.0, 1.0)  # 5+ документов = отличная доступность

    def _generate_success_recommendations(self, factors: Dict[str, float], probability: float) -> List[str]:
        """Генерация рекомендаций для улучшения успеха"""
        recommendations = []

        if factors and factors.get('query_clarity', 0) < 0.6:
            recommendations.append("Запросить уточнение у пользователя")
        if factors and factors.get('rag_confidence', 0) < 0.4:
            recommendations.append("Использовать дополнительные источники информации")
        if factors and factors.get('user_engagement', 0) < 0.5:
            recommendations.append("Увеличить интерактивность диалога")

        return recommendations

    # Дополнительные вспомогательные методы...
    def _get_club_creation_recommendations(self, user_profile: Dict[str, Any], rag_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [
            {
                'action': 'provide_step_by_step_guide',
                'description': 'Предоставить пошаговое руководство по созданию клуба',
                'priority': 'high',
                'automation_level': 'automated'
            }
        ]

    def _get_technical_help_recommendations(self, urgency: str) -> List[Dict[str, Any]]:
        priority = 'high' if urgency == 'high' else 'medium'
        return [
            {
                'action': 'provide_troubleshooting_steps',
                'description': 'Предоставить шаги для решения проблемы',
                'priority': priority,
                'automation_level': 'automated'
            }
        ]

    def _get_recommendation_actions(self, user_profile: Dict[str, Any], rag_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [
            {
                'action': 'analyze_user_preferences',
                'description': 'Проанализировать предпочтения пользователя для рекомендаций',
                'priority': 'medium',
                'automation_level': 'automated'
            }
        ]

    def _assess_response_relevance(self, context: Dict[str, Any]) -> float:
        return 0.7

    def _assess_response_speed(self, context: Dict[str, Any]) -> float:
        return 0.8

    def _assess_problem_resolution(self, context: Dict[str, Any]) -> float:
        return 0.6

    def _assess_user_sentiment(self, context: Dict[str, Any]) -> float:
        sentiment = context.get('current_message', {}).get('sentiment', 'neutral')
        if sentiment == 'positive':
            return 0.9
        elif sentiment == 'negative':
            return 0.3
        else:
            return 0.6

    def _assess_conversation_flow(self, context: Dict[str, Any]) -> float:
        return 0.7

    def _calculate_satisfaction_confidence(self, factors: Dict[str, float]) -> float:
        return 0.6

    def _get_improvement_suggestions(self, factors: Dict[str, float]) -> List[str]:
        suggestions = []
        if factors['response_relevance'] < 0.6:
            suggestions.append("Улучшить релевантность ответов")
        if factors['problem_resolution'] < 0.5:
            suggestions.append("Более полно решать проблемы пользователей")
        return suggestions

    def _get_user_interaction_patterns(self, user_id: int) -> List[Dict[str, Any]]:
        # Заглушка - в реальной реализации брать из базы данных
        return [{'hours_between': 24.0}]

    def _assess_query_resolution(self, context: Dict[str, Any]) -> float:
        return 0.7

    def _assess_user_engagement_level(self, context: Dict[str, Any]) -> float:
        return 0.6

    def _predict_next_topic(self, context: Dict[str, Any]) -> Optional[str]:
        return None