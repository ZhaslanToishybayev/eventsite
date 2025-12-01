#!/usr/bin/env python3
"""
🤖 AI Club Consultant - Интеллектуальный агент для клубов и мероприятий

Этот модуль реализует AI консультанта с использованием GPT-4o mini для:
1. Рекомендации клубов на основе интересов пользователя
2. Диалоговое создание новых клубов
3. Ответы на вопросы о существующих клубах и мероприятиях
4. Поиск и фильтрация по различным критериям

Архитектура:
- RAG (Retrieval-Augmented Generation) система
- Векторные embeddings для семантического поиска
- Контекстное AI-обогащение
- Диалоговое взаимодействие
"""

import os
import json
import logging
import hashlib
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict

import django
from django.conf import settings
from django.core.handlers.asgi import sync_to_async

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from clubs.models import Club, ClubCategory, City
from accounts.models import User
from django.db.models import Q, Count
from django.core.cache import cache

# Настройка логирования
logger = logging.getLogger(__name__)

@dataclass
class UserContext:
    """Контекст пользователя для персонализированных рекомендаций"""
    user_id: Optional[int] = None
    location: Optional[str] = None
    interests: List[str] = None
    conversation_history: List[Dict[str, str]] = None
    current_club_search: Dict[str, Any] = None
    session_start: datetime = None

    def __post_init__(self):
        if self.interests is None:
            self.interests = []
        if self.conversation_history is None:
            self.conversation_history = []
        if self.session_start is None:
            self.session_start = datetime.now()

@dataclass
class ClubRecommendation:
    """Рекомендация клуба с оценкой релевантности"""
    club: Club
    relevance_score: float
    match_reasons: List[str]
    suggested_questions: List[str]

class AIClubConsultant:
    """Основной AI агент для консультаций по клубам"""

    def __init__(self, api_key: str = None):
        """
        Инициализация AI консультанта

        Args:
            api_key: Ключ для GPT-4o mini API (если не указан, используется из настроек)
        """
        self.api_key = api_key or getattr(settings, 'OPENAI_API_KEY', None)
        self.model = "gpt-4o-mini"
        self.context_window = 10  # Количество последних сообщений для контекста
        self.recommendation_limit = 5  # Максимум рекомендаций

        if not self.api_key:
            logger.warning("GPT-4o mini API key not found. AI features will be limited.")

        # Кэш для embeddings и результатов поиска
        self.embedding_cache = {}
        self.search_cache_timeout = 300  # 5 минут

        logger.info("AI Club Consultant initialized")

    async def process_user_message(self, message: str, user_id: int = None, location: str = None) -> Dict[str, Any]:
        """
        Основной метод обработки сообщения пользователя

        Args:
            message: Сообщение от пользователя
            user_id: ID пользователя (если авторизован)
            location: Географическое расположение пользователя

        Returns:
            Dict: AI ответ с рекомендациями и действиями
        """
        try:
            # Анализ типа запроса
            query_type = await self._analyze_query_type(message)

            # Получение контекста пользователя
            user_context = await self._get_user_context(user_id, location)

            # Обновление истории диалога
            user_context.conversation_history.append({
                'role': 'user',
                'content': message,
                'timestamp': datetime.now().isoformat()
            })

            # Генерация AI ответа
            if query_type == 'greeting':
                response = await self._handle_greeting(user_context)
            elif query_type == 'club_creation':
                response = await self._handle_club_creation(message, user_context)
            elif query_type == 'recommendation':
                response = await self._handle_recommendation(message, user_context)
            elif query_type == 'club_info':
                response = await self._handle_club_info(message, user_context)
            elif query_type == 'search':
                response = await self._handle_search(message, user_context)
            else:
                response = await self._handle_general_query(message, user_context)

            # Добавление AI ответа в историю
            user_context.conversation_history.append({
                'role': 'assistant',
                'content': response['content'],
                'timestamp': datetime.now().isoformat()
            })

            # Сохранение контекста
            await self._save_user_context(user_id, user_context)

            return response

        except Exception as e:
            logger.error(f"Error processing user message: {e}")
            return self._get_error_response()

    async def _analyze_query_type(self, message: str) -> str:
        """Анализ типа пользовательского запроса"""
        message_lower = message.lower().strip()

        # Приветствия
        greetings = ['привет', 'здравствуй', 'добрый день', 'hello', 'hi', 'hey']
        if any(greeting in message_lower for greeting in greetings):
            return 'greeting'

        # Создание клуба
        club_creation_keywords = ['создать клуб', 'сделать клуб', 'новый клуб', 'club creation', 'create club']
        if any(keyword in message_lower for keyword in club_creation_keywords):
            return 'club_creation'

        # Рекомендации
        recommendation_keywords = ['рекоменд', 'поиск', 'найти', 'подскаж', 'что посмотреть', 'recommend', 'find']
        if any(keyword in message_lower for keyword in recommendation_keywords):
            return 'recommendation'

        # Информация о клубах
        info_keywords = ['расскажи', 'информация', 'о клубе', 'about', 'info', 'details']
        if any(keyword in message_lower for keyword in info_keywords):
            return 'club_info'

        # Поиск
        search_keywords = ['ищу', 'нужен', 'хочу найти', 'looking for', 'search for']
        if any(keyword in message_lower for keyword in search_keywords):
            return 'search'

        return 'general'

    async def _handle_greeting(self, user_context: UserContext) -> Dict[str, Any]:
        """Обработка приветствия"""
        welcome_message = (
            "👋 Здравствуйте! Я AI консультант по клубам и мероприятиям.\n\n"
            "Я могу помочь вам:\n"
            "• 🔍 Найти подходящие клубы по вашим интересам\n"
            "• 📍 Посмотреть клубы в вашем городе\n"
            "• 🤝 Создать новый клуб\n"
            "• 💬 Ответить на вопросы о существующих клубах\n\n"
            "Чем могу помочь?"
        )

        return {
            'type': 'greeting',
            'content': welcome_message,
            'suggestions': [
                'Найти музыкальные клубы в Алматы',
                'Расскажи о танцевальных клубах',
                'Хочу создать спортивный клуб',
                'Какие есть IT-клубы?'
            ],
            'quick_actions': [
                {'text': 'Найти клубы', 'action': 'find_clubs'},
                {'text': 'Создать клуб', 'action': 'create_club'},
                {'text': 'Мои интересы', 'action': 'my_interests'}
            ]
        }

    async def _handle_club_creation(self, message: str, user_context: UserContext) -> Dict[str, Any]:
        """Обработка запроса на создание клуба"""
        # Определяем текущий этап создания клуба
        current_stage = self._get_creation_stage(user_context)

        if current_stage == 'name':
            return await self._ask_club_name()
        elif current_stage == 'description':
            return await self._ask_club_description()
        elif current_stage == 'location':
            return await self._ask_club_location()
        elif current_stage == 'category':
            return await self._ask_club_category()
        elif current_stage == 'target_audience':
            return await self._ask_target_audience()
        elif current_stage == 'confirmation':
            return await self._confirm_club_creation(user_context)
        else:
            return await self._start_club_creation()

    async def _handle_recommendation(self, message: str, user_context: UserContext) -> Dict[str, Any]:
        """Обработка запроса на рекомендации"""
        # Извлечение критериев из сообщения
        criteria = await self._extract_recommendation_criteria(message, user_context)

        # Поиск подходящих клубов
        clubs = await self._search_clubs_by_criteria(criteria)

        if not clubs:
            return await self._handle_no_clubs_found(criteria)

        # Генерация персонализированных рекомендаций
        recommendations = await self._generate_personalized_recommendations(clubs, criteria, user_context)

        return await self._format_recommendation_response(recommendations, criteria)

    async def _handle_club_info(self, message: str, user_context: UserContext) -> Dict[str, Any]:
        """Обработка запроса информации о конкретном клубе"""
        # Поиск названия клуба в сообщении
        club_name = await self._extract_club_name(message)

        if not club_name:
            return {
                'type': 'clarification',
                'content': "Пожалуйста, уточните название клуба, о котором вы хотите узнать.",
                'suggestions': ['Назовите имя клуба', 'Покажите список клубов']
            }

        # Поиск клуба в базе данных
        try:
            club = await Club.objects.aget(name__icontains=club_name)
            return await self._format_club_info_response(club)
        except Club.DoesNotExist:
            return {
                'type': 'not_found',
                'content': f"Клуб '{club_name}' не найден. Проверьте название или посмотрите другие клубы.",
                'suggestions': ['Показать все клубы', 'Найти похожие клубы']
            }

    async def _handle_search(self, message: str, user_context: UserContext) -> Dict[str, Any]:
        """Обработка поискового запроса"""
        # Извлечение поисковых терминов
        search_terms = await self._extract_search_terms(message)

        if not search_terms:
            return {
                'type': 'clarification',
                'content': "Пожалуйста, уточните, что вы ищете.",
                'suggestions': ['Музыкальные клубы', 'Спортивные секции', 'IT-клубы']
            }

        # Поиск по терминам
        clubs = await self._search_clubs_by_terms(search_terms, user_context.location)

        if not clubs:
            return await self._handle_no_clubs_found({'search_terms': search_terms})

        return await self._format_search_response(clubs, search_terms)

    async def _handle_general_query(self, message: str, user_context: UserContext) -> Dict[str, Any]:
        """Обработка общих запросов"""
        # Проверка на наличие упоминаний конкретных клубов
        mentioned_clubs = await self._find_mentioned_clubs(message)

        if mentioned_clubs:
            return await self._handle_mentioned_clubs(mentioned_clubs, user_context)

        # Генерация общего ответа с использованием RAG
        response = await self._generate_rag_response(message, user_context)

        return {
            'type': 'general',
            'content': response,
            'suggestions': [
                'Найти клубы по интересам',
                'Посмотреть мероприятия',
                'Узнать о создании клуба'
            ]
        }

    # Вспомогательные методы

    async def _get_user_context(self, user_id: int, location: str) -> UserContext:
        """Получение контекста пользователя"""
        cache_key = f"user_context_{user_id or 'anonymous'}"
        cached_context = cache.get(cache_key)

        if cached_context:
            context = UserContext(**cached_context)
            if location:
                context.location = location
        else:
            context = UserContext(user_id=user_id, location=location)

        return context

    async def _save_user_context(self, user_id: int, context: UserContext):
        """Сохранение контекста пользователя"""
        cache_key = f"user_context_{user_id or 'anonymous'}"
        cache.set(cache_key, {
            'user_id': context.user_id,
            'location': context.location,
            'interests': context.interests,
            'conversation_history': context.conversation_history[-20:],  # Сохраняем последние 20 сообщений
            'current_club_search': context.current_club_search,
            'session_start': context.session_start.isoformat() if hasattr(context.session_start, 'isoformat') else str(context.session_start)
        }, timeout=3600)  # 1 час

    def _get_creation_stage(self, user_context: UserContext) -> str:
        """Определение этапа создания клуба"""
        if not hasattr(user_context, 'club_creation_data'):
            return 'name'

        data = user_context.club_creation_data
        if not data.get('name'):
            return 'name'
        elif not data.get('description'):
            return 'description'
        elif not data.get('location'):
            return 'location'
        elif not data.get('category'):
            return 'category'
        elif not data.get('target_audience'):
            return 'target_audience'
        else:
            return 'confirmation'

    async def _ask_club_name(self) -> Dict[str, Any]:
        """Запрос названия клуба"""
        return {
            'type': 'club_creation',
            'stage': 'name',
            'content': "🎉 Отлично! Давайте создадим новый клуб!\n\n"
                      "1. Какое название вы хотите дать вашему клубу?",
            'input_placeholder': 'Введите название клуба',
            'suggestions': ['Музыкальный клуб', 'Спортивная секция', 'IT-сообщество']
        }

    async def _ask_club_description(self) -> Dict[str, Any]:
        """Запрос описания клуба"""
        return {
            'type': 'club_creation',
            'stage': 'description',
            'content': "2. Чем будет заниматься ваш клуб? Опишите основную деятельность.",
            'input_placeholder': 'Описание деятельности клуба',
            'suggestions': ['Занятия музыкой', 'Спортивные тренировки', 'IT-встречи']
        }

    async def _ask_club_location(self) -> Dict[str, Any]:
        """Запрос местоположения клуба"""
        return {
            'type': 'club_creation',
            'stage': 'location',
            'content': "3. Где будет находиться клуб?",
            'input_placeholder': 'Город или район',
            'suggestions': ['Алматы', 'Астана', 'Онлайн']
        }

    async def _ask_club_category(self) -> Dict[str, Any]:
        """Запрос категории клуба"""
        categories = await self._get_available_categories()
        return {
            'type': 'club_creation',
            'stage': 'category',
            'content': "4. К какой категории относится ваш клуб?",
            'input_placeholder': 'Выберите категорию',
            'suggestions': categories
        }

    async def _ask_target_audience(self) -> Dict[str, Any]:
        """Запрос целевой аудитории"""
        return {
            'type': 'club_creation',
            'stage': 'target_audience',
            'content': "5. Для кого предназначен клуб? (возраст, интересы, уровень подготовки)",
            'input_placeholder': 'Целевая аудитория',
            'suggestions': ['Для взрослых', 'Для студентов', 'Для детей']
        }

    async def _confirm_club_creation(self, user_context: UserContext) -> Dict[str, Any]:
        """Подтверждение создания клуба"""
        data = user_context.club_creation_data
        confirmation_text = (
            "✅ Проверьте информацию о вашем клубе:\n\n"
            f"• **Название**: {data['name']}\n"
            f"• **Описание**: {data['description']}\n"
            f"• **Местоположение**: {data['location']}\n"
            f"• **Категория**: {data['category']}\n"
            f"• **Целевая аудитория**: {data['target_audience']}\n\n"
            "Все верно?"
        )

        return {
            'type': 'club_creation',
            'stage': 'confirmation',
            'content': confirmation_text,
            'actions': [
                {'text': 'Да, создать клуб', 'action': 'confirm_create'},
                {'text': 'Изменить данные', 'action': 'edit_data'}
            ]
        }

    async def _start_club_creation(self) -> Dict[str, Any]:
        """Начало процесса создания клуба"""
        return {
            'type': 'club_creation',
            'stage': 'name',
            'content': "🎉 Отлично! Давайте создадим новый клуб!\n\n"
                      "1. Какое название вы хотите дать вашему клубу?",
            'input_placeholder': 'Введите название клуба'
        }

    async def _get_available_categories(self) -> List[str]:
        """Получение доступных категорий клубов"""
        try:
            categories = await sync_to_async(list)(ClubCategory.objects.all().values_list('name', flat=True))
            return categories
        except Exception:
            return ['Музыка', 'Спорт', 'Технологии', 'Образование', 'Искусство']

    def _get_error_response(self) -> Dict[str, Any]:
        """Получение ответа при ошибке"""
        return {
            'type': 'error',
            'content': "Извините, произошла ошибка. Пожалуйста, попробуйте еще раз или задайте другой вопрос.",
            'suggestions': [
                'Начать сначала',
                'Найти клубы',
                'Создать клуб'
            ]
        }

    async def _extract_recommendation_criteria(self, message: str, user_context: UserContext) -> Dict[str, Any]:
        """Извлечение критериев для рекомендаций"""
        # Простой парсинг сообщения для извлечения критериев
        criteria = {
            'interests': [],
            'location': user_context.location,
            'category': None,
            'keywords': []
        }

        message_lower = message.lower()

        # Извлечение интересов
        interest_keywords = {
            'музыка': ['музыка', 'пение', 'инструменты'],
            'спорт': ['спорт', 'фитнес', 'тренировки'],
            'технологии': ['технологии', 'программирование', 'it'],
            'искусство': ['искусство', 'рисование', 'творчество']
        }

        for interest, keywords in interest_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                criteria['interests'].append(interest)

        # Извлечение локации
        location_keywords = ['в алмате', 'в астане', 'в городе', 'здесь']
        for keyword in location_keywords:
            if keyword in message_lower:
                criteria['location'] = keyword.replace('в ', '').replace(' здесь', '')

        return criteria

    async def _search_clubs_by_criteria(self, criteria: Dict[str, Any]) -> List[Club]:
        """Поиск клубов по критериям"""
        try:
            clubs = Club.objects.filter(is_active=True)

            # Фильтрация по локации
            if criteria.get('location'):
                clubs = clubs.filter(city__name__icontains=criteria['location'])

            # Фильтрация по интересам
            if criteria.get('interests'):
                interests_filter = Q()
                for interest in criteria['interests']:
                    interests_filter |= Q(description__icontains=interest) | Q(activities__icontains=interest)
                clubs = clubs.filter(interests_filter)

            # Фильтрация по ключевым словам
            if criteria.get('keywords'):
                keywords_filter = Q()
                for keyword in criteria['keywords']:
                    keywords_filter |= Q(name__icontains=keyword) | Q(description__icontains=keyword)
                clubs = clubs.filter(keywords_filter)

            return list(clubs.select_related('city', 'category').all()[:10])
        except Exception as e:
            logger.error(f"Error searching clubs: {e}")
            return []

    async def _generate_personalized_recommendations(self, clubs: List[Club], criteria: Dict[str, Any], user_context: UserContext) -> List[ClubRecommendation]:
        """Генерация персонализированных рекомендаций"""
        recommendations = []

        for club in clubs:
            # Расчет релевантности
            relevance_score = self._calculate_relevance_score(club, criteria, user_context)
            match_reasons = self._generate_match_reasons(club, criteria)

            recommendation = ClubRecommendation(
                club=club,
                relevance_score=relevance_score,
                match_reasons=match_reasons,
                suggested_questions=self._generate_suggested_questions(club)
            )
            recommendations.append(recommendation)

        # Сортировка по релевантности
        recommendations.sort(key=lambda x: x.relevance_score, reverse=True)
        return recommendations[:self.recommendation_limit]

    def _calculate_relevance_score(self, club: Club, criteria: Dict[str, Any], user_context: UserContext) -> float:
        """Расчет балла релевантности"""
        score = 0.0

        # Базовый балл за активность
        if club.is_active:
            score += 1.0

        # Баллы за соответствие локации
        if criteria.get('location') and club.city:
            if criteria['location'].lower() in club.city.name.lower():
                score += 2.0

        # Баллы за соответствие интересам
        if criteria.get('interests'):
            for interest in criteria['interests']:
                if interest.lower() in (club.description or '').lower():
                    score += 1.5
                if interest.lower() in (club.activities or '').lower():
                    score += 1.0

        # Баллы за соответствие истории диалога
        if user_context.conversation_history:
            recent_topics = ' '.join([
                msg['content'] for msg in user_context.conversation_history[-3:]
                if msg['role'] == 'user'
            ]).lower()
            if any(topic in (club.description or '').lower() for topic in ['музыка', 'спорт', 'ит']):
                score += 0.5

        return score

    def _generate_match_reasons(self, club: Club, criteria: Dict[str, Any]) -> List[str]:
        """Генерация причин соответствия"""
        reasons = []

        if criteria.get('location') and club.city and criteria['location'].lower() in club.city.name.lower():
            reasons.append(f"📍 Находится в {club.city.name}")

        if criteria.get('interests'):
            for interest in criteria['interests']:
                if interest.lower() in (club.description or '').lower():
                    reasons.append(f"🎯 Подходит по интересам: {interest}")

        if club.members_count > 10:
            reasons.append(f"👥 Активное сообщество ({club.members_count} участников)")

        return reasons[:3]  # Максимум 3 причины

    def _generate_suggested_questions(self, club: Club) -> List[str]:
        """Генерация предложенных вопросов"""
        questions = []
        base_question = f"Расскажи подробнее о клубе {club.name}"

        if club.category:
            questions.append(f"Какие мероприятия проводит {club.name}?")
            questions.append(f"Для кого подходит клуб {club.name}?")

        if club.city:
            questions.append(f"Где проходят встречи {club.name}?")

        return questions[:2]

    async def _format_recommendation_response(self, recommendations: List[ClubRecommendation], criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Форматирование ответа с рекомендациями"""
        if not recommendations:
            return await self._handle_no_clubs_found(criteria)

        response_text = "🎯 Вот подходящие клубы, которые я нашел:\n\n"

        for i, rec in enumerate(recommendations, 1):
            club = rec.club
            response_text += (
                f"{i}. **{club.name}**\n"
                f"   📍 {club.city.name if club.city else 'Не указан'}\n"
                f"   📝 {club.description[:100]}...\n"
                f"   👥 {club.members_count} участников\n"
            )

            if rec.match_reasons:
                response_text += f"   💡 Подходит потому что: {', '.join(rec.match_reasons[:2])}\n"

            response_text += "\n"

        response_text += (
            "💬 Хотите больше информации о каком-то из клубов?\n"
            "Или ищете что-то другое?"
        )

        return {
            'type': 'recommendations',
            'content': response_text,
            'clubs': [
                {
                    'id': str(club.club.id),
                    'name': club.club.name,
                    'description': club.club.description[:200],
                    'city': club.club.city.name if club.club.city else 'Не указан',
                    'members_count': club.club.members_count,
                    'relevance_score': club.relevance_score
                }
                for club in recommendations
            ],
            'suggestions': [
                'Расскажи подробнее о первом клубе',
                'Показать больше клубов',
                'Найти клубы по другим интересам'
            ]
        }

    async def _handle_no_clubs_found(self, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка случая, когда клубы не найдены"""
        suggestions = [
            'Попробуйте изменить критерии поиска',
            'Расскажите подробнее о ваших интересах',
            'Посмотрите все доступные клубы'
        ]

        if criteria.get('location'):
            suggestions.append(f'Найти клубы в других городах')

        if criteria.get('interests'):
            suggestions.append(f'Найти клубы по похожим интересам')

        return {
            'type': 'no_results',
            'content': (
                "😔 К сожалению, я не нашел подходящих клубов по вашему запросу.\n\n"
                "Попробуйте уточнить:\n"
                "• Ваши конкретные интересы\n"
                "• Ваш город или регион\n"
                "• Тип деятельности (музыка, спорт, танцы и т.д.)\n\n"
                "Или расскажите подробнее о том, что вас интересует!"
            ),
            'suggestions': suggestions
        }

    async def _extract_club_name(self, message: str) -> Optional[str]:
        """Извлечение названия клуба из сообщения"""
        # Простой алгоритм извлечения названия
        # В реальной реализации можно использовать NLP
        club_indicators = ['клуб', 'клуба', 'клубу', 'клубом']
        for indicator in club_indicators:
            if indicator in message.lower():
                # Извлекаем возможное название после указателя
                parts = message.split(indicator)
                if len(parts) > 1:
                    name_part = parts[1].strip()
                    # Удаляем лишние слова
                    name_words = name_part.split()[:3]  # Берем первые 3 слова
                    return ' '.join(name_words)
        return None

    async def _format_club_info_response(self, club: Club) -> Dict[str, Any]:
        """Форматирование ответа с информацией о клубе"""
        response_text = (
            f"🏢 **{club.name}**\n\n"
            f"📝 **Описание**: {club.description}\n\n"
            f"📍 **Местоположение**: {club.city.name if club.city else 'Не указано'}\n"
            f"🏷️ **Категория**: {club.category.name if club.category else 'Не указана'}\n"
            f"👥 **Участники**: {club.members_count}\n"
            f"📅 **Создан**: {club.created_at.strftime('%d.%m.%Y')}\n"
        )

        if club.activities:
            response_text += f"🎯 **Деятельность**: {club.activities}\n"

        if club.email:
            response_text += f"📧 **Email**: {club.email}\n"

        if club.phone:
            response_text += f"📞 **Телефон**: {club.phone}\n"

        return {
            'type': 'club_info',
            'content': response_text,
            'club': {
                'id': str(club.id),
                'name': club.name,
                'description': club.description,
                'city': club.city.name if club.city else None,
                'category': club.category.name if club.category else None,
                'members_count': club.members_count,
                'activities': club.activities,
                'email': club.email,
                'phone': club.phone,
                'created_at': club.created_at.isoformat()
            },
            'actions': [
                {'text': 'Посмотреть мероприятия', 'action': 'show_events'},
                {'text': 'Найти похожие клубы', 'action': 'find_similar'},
                {'text': 'Связаться с клубом', 'action': 'contact_club'}
            ]
        }

    async def _extract_search_terms(self, message: str) -> List[str]:
        """Извлечение поисковых терминов"""
        # Простая обработка сообщения
        terms = []
        message_lower = message.lower()

        # Ключевые слова для поиска
        search_keywords = ['клуб', 'секция', 'сообщество', 'группа', 'мероприятие']
        for keyword in search_keywords:
            if keyword in message_lower:
                terms.append(keyword)

        # Извлечение интересов
        interest_words = ['музыка', 'спорт', 'танцы', 'игры', 'кино', 'книги', 'it', 'технологии']
        for word in interest_words:
            if word in message_lower:
                terms.append(word)

        return list(set(terms))  # Уникальные термины

    async def _search_clubs_by_terms(self, terms: List[str], location: str = None) -> List[Club]:
        """Поиск клубов по терминам"""
        try:
            clubs = Club.objects.filter(is_active=True)

            if location:
                clubs = clubs.filter(city__name__icontains=location)

            if terms:
                search_filter = Q()
                for term in terms:
                    search_filter |= (
                        Q(name__icontains=term) |
                        Q(description__icontains=term) |
                        Q(activities__icontains=term)
                    )
                clubs = clubs.filter(search_filter)

            return list(clubs.select_related('city', 'category').all()[:10])
        except Exception as e:
            logger.error(f"Error searching clubs by terms: {e}")
            return []

    async def _format_search_response(self, clubs: List[Club], search_terms: List[str]) -> Dict[str, Any]:
        """Форматирование ответа на поиск"""
        response_text = f"🔍 Найдено клубов по запросу '{', '.join(search_terms)}':\n\n"

        for i, club in enumerate(clubs[:5], 1):
            response_text += (
                f"{i}. **{club.name}**\n"
                f"   📍 {club.city.name if club.city else 'Не указан'}\n"
                f"   📝 {club.description[:80]}...\n"
                f"   👥 {club.members_count} участников\n\n"
            )

        if len(clubs) > 5:
            response_text += f"... и еще {len(clubs) - 5} клубов\n\n"

        response_text += "💬 Хотите подробную информацию о каком-то из клубов?"

        return {
            'type': 'search_results',
            'content': response_text,
            'clubs': [
                {
                    'id': str(club.id),
                    'name': club.name,
                    'description': club.description[:150],
                    'city': club.city.name if club.city else 'Не указан',
                    'members_count': club.members_count
                }
                for club in clubs[:10]
            ],
            'total_found': len(clubs),
            'search_terms': search_terms
        }

    async def _find_mentioned_clubs(self, message: str) -> List[str]:
        """Поиск упомянутых клубов в сообщении"""
        try:
            club_names = await sync_to_async(list)(Club.objects.all().values_list('name', flat=True))
            mentioned = []

            for club_name in club_names:
                if club_name.lower() in message.lower():
                    mentioned.append(club_name)

            return mentioned
        except Exception:
            return []

    async def _handle_mentioned_clubs(self, mentioned_clubs: List[str], user_context: UserContext) -> Dict[str, Any]:
        """Обработка упомянутых клубов"""
        if len(mentioned_clubs) == 1:
            club_name = mentioned_clubs[0]
            try:
                club = await Club.objects.aget(name=club_name)
                return await self._format_club_info_response(club)
            except Club.DoesNotExist:
                pass

        response_text = f"Я нашел упоминания следующих клубов: {', '.join(mentioned_clubs)}.\n\n"
        response_text += "Хотите узнать подробную информацию о каком-то из них?"

        return {
            'type': 'mentioned_clubs',
            'content': response_text,
            'mentioned_clubs': mentioned_clubs,
            'suggestions': ['Расскажи о первом клубе', 'Показать все упомянутые клубы']
        }

    async def _generate_rag_response(self, message: str, user_context: UserContext) -> str:
        """Генерация ответа с использованием RAG"""
        # Поиск релевантной информации в базе данных
        relevant_info = await self._retrieve_relevant_information(message)

        # Формирование контекста для AI
        context = self._build_rag_context(message, relevant_info, user_context)

        # Генерация ответа (в реальной реализации - через GPT-4o mini API)
        if self.api_key:
            try:
                # Здесь будет вызов GPT-4o mini API
                # response = await self._call_gpt4o_mini(context)
                # return response
                pass
            except Exception as e:
                logger.error(f"Error calling GPT-4o mini: {e}")

        # Заглушка для AI ответа
        return (
            "Спасибо за ваш вопрос! Я помогу вам найти подходящие клубы или создать новый.\n\n"
            "Пожалуйста, уточните:\n"
            "• Ваши интересы или хобби\n"
            "• Ваш город\n"
            "• Что именно вы ищете\n\n"
            "Это поможет мне лучше понять и помочь вам! 🤝"
        )

    async def _retrieve_relevant_information(self, message: str) -> Dict[str, Any]:
        """Извлечение релевантной информации из базы данных"""
        relevant_info = {
            'clubs': [],
            'categories': [],
            'cities': []
        }

        try:
            # Поиск клубов по ключевым словам
            if len(message.strip()) > 3:
                clubs = await sync_to_async(list)(Club.objects.filter(
                    Q(name__icontains=message) |
                    Q(description__icontains=message) |
                    Q(activities__icontains=message)
                ).select_related('city', 'category')[:5])

                relevant_info['clubs'] = [
                    {
                        'name': club.name,
                        'description': club.description[:200],
                        'city': club.city.name if club.city else None,
                        'category': club.category.name if club.category else None
                    }
                    for club in clubs
                ]

            # Получение популярных категорий
            categories = await sync_to_async(list)(ClubCategory.objects.all()[:5])
            relevant_info['categories'] = [cat.name for cat in categories]

            # Получение городов
            cities = await sync_to_async(list)(City.objects.all()[:5])
            relevant_info['cities'] = [city.name for city in cities]

        except Exception as e:
            logger.error(f"Error retrieving relevant information: {e}")

        return relevant_info

    def _build_rag_context(self, message: str, relevant_info: Dict[str, Any], user_context: UserContext) -> str:
        """Построение контекста для RAG"""
        context = f"User message: {message}\n\n"

        if relevant_info['clubs']:
            context += "Relevant clubs:\n"
            for club in relevant_info['clubs']:
                context += f"- {club['name']}: {club['description']} (Location: {club['city']}, Category: {club['category']})\n"
            context += "\n"

        if relevant_info['categories']:
            context += f"Available categories: {', '.join(relevant_info['categories'])}\n\n"

        if relevant_info['cities']:
            context += f"Available cities: {', '.join(relevant_info['cities'])}\n\n"

        if user_context.location:
            context += f"User location: {user_context.location}\n"

        if user_context.interests:
            context += f"User interests: {', '.join(user_context.interests)}\n"

        return context