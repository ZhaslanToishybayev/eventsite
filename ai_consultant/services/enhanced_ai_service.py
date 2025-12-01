"""
🤖 Enhanced AI Consultant Service
Улучшенный AI сервис для работы с клубами, поиском и рекомендациями
"""

import json
import logging
import re
from typing import List, Dict, Any, Optional, Tuple
from django.db.models import Q, Count, Case, When, IntegerField
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta

from clubs.models import Club, ClubCategory, City, UserInterest
from ai_consultant.services.openai_client import OpenAIClientService
from ai_consultant.services.rag_service import get_rag_service

logger = logging.getLogger('ai_consultant')

class EnhancedAIConsultantService:
    """Улучшенный AI сервис для консультаций по клубам"""

    def __init__(self):
        self.openai_client = OpenAIClientService()
        self.rag_service = get_rag_service()

    def analyze_user_query(self, message: str) -> Dict[str, Any]:
        """
        Анализирует запрос пользователя и определяет тип запроса

        Args:
            message: Текст сообщения от пользователя

        Returns:
            Dict: Результат анализа с типом запроса и извлеченными параметрами
        """
        message_lower = message.lower().strip()

        # Определение типа запроса
        if any(keyword in message_lower for keyword in [
            'создать клуб', 'создай клуб', 'хочу создать', 'создание клуба',
            'зарегистрировать клуб', 'основать клуб', 'создать сообщество'
        ]):
            return {
                'intent': 'club_creation',
                'parameters': self._extract_club_creation_params(message)
            }

        elif any(keyword in message_lower for keyword in [
            'найти клуб', 'поиск клуб', 'поищ', 'клубы', 'сообщества',
            'найти сообщество', 'поиск сообществ', 'рекомендуй клуб',
            'порекомендуй', 'что посоветуешь', 'что посоветуете'
        ]):
            return {
                'intent': 'club_search',
                'parameters': self._extract_search_params(message)
            }

        elif any(keyword in message_lower for keyword in [
            'расскажи о', 'что такое', 'расскажи про', 'расскажите о',
            'информация о', 'описание', 'чем занимается'
        ]):
            return {
                'intent': 'club_info',
                'parameters': self._extract_club_info_params(message)
            }

        elif any(keyword in message_lower for keyword in [
            'привет', 'здравствуй', 'добрый день', 'хай', 'hello', 'hi'
        ]):
            return {
                'intent': 'greeting',
                'parameters': {}
            }

        else:
            return {
                'intent': 'general_chat',
                'parameters': {}
            }

    def _extract_club_creation_params(self, message: str) -> Dict[str, Any]:
        """Извлекает параметры для создания клуба"""
        params = {}

        # Поиск названия клуба
        name_patterns = [
            r'называется\s+([А-Яа-я\w\s]+?)(?:,|$|\.|,|\s+(?:но|и|а|но|для))',
            r'клуб\s+([А-Яа-я\w\s]+?)(?:,|$|\.|,|\s+(?:но|и|а|но|для))',
            r'"([^"]+)"',
            r"'([^']+)'"
        ]

        for pattern in name_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                params['club_name'] = match.group(1).strip()
                break

        # Поиск интересов/направлений
        interest_keywords = [
            'спорт', 'здоровье', 'фитнес', 'образование', 'учеба', 'технологии',
            'ит', 'программирование', 'музыка', 'искусство', 'творчество',
            'бизнес', 'предпринимательство', 'языки', 'путешествия',
            'игры', 'гейминг', 'книги', 'чтение', 'фильмы', 'кино'
        ]

        found_interests = []
        for interest in interest_keywords:
            if interest in message.lower():
                found_interests.append(interest)

        if found_interests:
            params['interests'] = found_interests

        return params

    def _extract_search_params(self, message: str) -> Dict[str, Any]:
        """Извлекает параметры поиска клубов"""
        params = {}

        # Поиск города
        cities = City.objects.values_list('name', flat=True)
        for city in cities:
            if city.lower() in message.lower():
                params['city'] = city
                break

        # Поиск категорий
        categories = ClubCategory.objects.filter(is_active=True).values_list('name', flat=True)
        for category in categories:
            if category.lower() in message.lower():
                params['category'] = category
                break

        # Поиск интересов
        interest_keywords = [
            'спорт', 'здоровье', 'фитнес', 'образование', 'учеба', 'технологии',
            'ит', 'программирование', 'музыка', 'искусство', 'творчество',
            'бизнес', 'предпринимательство', 'языки', 'путешествия',
            'игры', 'гейминг', 'книги', 'чтение', 'фильмы', 'кино',
            'танцы', 'йога', 'медицина', 'кулинария', 'фотография'
        ]

        found_interests = []
        for interest in interest_keywords:
            if interest in message.lower():
                found_interests.append(interest)

        if found_interests:
            params['interests'] = found_interests

        # Поиск количества
        count_patterns = [
            r'(\d+)\s*(?:клуб|сообщество|групп)',
            r'показать\s+(\d+)',
            r'найди\s+(\d+)',
        ]

        for pattern in count_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                params['limit'] = min(int(match.group(1)), 10)  # Максимум 10
                break

        if 'limit' not in params:
            params['limit'] = 5  # По умолчанию 5

        return params

    def _extract_club_info_params(self, message: str) -> Dict[str, Any]:
        """Извлекает параметры для получения информации о клубе"""
        params = {}

        # Поиск названия клуба
        club_names = Club.objects.filter(is_active=True).values_list('name', flat=True)
        for club_name in club_names:
            if club_name.lower() in message.lower():
                params['club_name'] = club_name
                break

        return params

    def search_clubs(self, search_params: Dict[str, Any], limit: int = 5) -> List[Club]:
        """
        Ищет клубы по заданным параметрам

        Args:
            search_params: Параметры поиска
            limit: Максимальное количество результатов

        Returns:
            List[Club]: Список подходящих клубов
        """
        queryset = Club.objects.filter(is_active=True)

        # Фильтрация по городу
        if 'city' in search_params:
            queryset = queryset.filter(city__name__icontains=search_params['city'])

        # Фильтрация по категории
        if 'category' in search_params:
            queryset = queryset.filter(category__name__icontains=search_params['category'])

        # Фильтрация по интересам (через теги)
        if 'interests' in search_params:
            interests = search_params['interests']
            q_objects = Q()
            for interest in interests:
                q_objects |= Q(tags__icontains=interest) | Q(description__icontains=interest)
            queryset = queryset.filter(q_objects)

        # Сортировка: сначала рекомендуемые, потом по популярности
        queryset = queryset.annotate(
            is_featured_weight=Case(
                When(is_featured=True, then=3),
                default=0,
                output_field=IntegerField()
            ),
            popularity_score=Case(
                When(members_count__gte=50, then=2),
                When(members_count__gte=20, then=1),
                default=0,
                output_field=IntegerField()
            )
        ).order_by('-is_featured_weight', '-popularity_score', '-members_count', '-likes_count')

        return list(queryset[:limit])

    def get_club_recommendations(self, user_interests: List[str], limit: int = 5) -> List[Club]:
        """
        Получает рекомендации клубов на основе интересов пользователя

        Args:
            user_interests: Интересы пользователя
            limit: Максимальное количество рекомендаций

        Returns:
            List[Club]: Рекомендованные клубы
        """
        if not user_interests:
            # Если нет интересов, возвращаем популярные клубы
            return list(Club.objects.filter(
                is_active=True,
                is_featured=True
            ).order_by('-members_count', '-likes_count')[:limit])

        # Поиск клубов по интересам
        queryset = Club.objects.filter(is_active=True)

        # Создаем веса для каждого клуба на основе соответствия интересам
        club_scores = []

        for club in queryset:
            score = 0

            # Проверка тегов
            if club.tags:
                club_tags = [tag.strip().lower() for tag in club.tags.split(',')]
                for interest in user_interests:
                    if interest.lower() in club_tags:
                        score += 3

            # Проверка описания
            if club.description:
                description_lower = club.description.lower()
                for interest in user_interests:
                    if interest.lower() in description_lower:
                        score += 1

            # Проверка целевой аудитории
            if club.target_audience:
                target_lower = club.target_audience.lower()
                for interest in user_interests:
                    if interest.lower() in target_lower:
                        score += 2

            # Бонус за популярность
            if club.is_featured:
                score += 2
            score += min(club.members_count // 10, 5)  # Бонус за популярность

            if score > 0:
                club_scores.append((club, score))

        # Сортируем по scores и возвращаем топ
        club_scores.sort(key=lambda x: x[1], reverse=True)
        return [club for club, score in club_scores[:limit]]

    def get_club_info(self, club_name: str) -> Optional[Club]:
        """Получает информацию о конкретном клубе"""
        try:
            return Club.objects.get(name__icontains=club_name, is_active=True)
        except Club.DoesNotExist:
            return None

    def format_club_info(self, club: Club) -> str:
        """Форматирует информацию о клубе для вывода пользователю"""
        info_parts = [
            f"🏆 *{club.name}*",
            f"📂 Категория: {club.category.name}",
            f"📍 Город: {club.city.name if club.city else 'Не указан'}",
            f"👥 Участников: {club.members_count}",
            f"❤️ Лайков: {club.likes_count}",
        ]

        if club.address and club.address != 'No location':
            info_parts.append(f"🗺️ Адрес: {club.address}")

        if club.tags:
            info_parts.append(f"🏷️ Теги: {club.tags}")

        if club.description:
            # Обрезаем описание до 300 символов
            description = club.description[:300]
            if len(club.description) > 300:
                description += "..."
            info_parts.append(f"📝 Описание: {description}")

        if club.target_audience:
            audience = club.target_audience[:150]
            if len(club.target_audience) > 150:
                audience += "..."
            info_parts.append(f"🎯 Целевая аудитория: {audience}")

        if club.activities:
            activities = club.activities[:200]
            if len(club.activities) > 200:
                activities += "..."
            info_parts.append(f"🎉 Мероприятия: {activities}")

        if club.email:
            info_parts.append(f"📧 Email: {club.email}")

        if club.phone:
            info_parts.append(f"📞 Телефон: {club.phone}")

        return "\n".join(info_parts)

    def generate_ai_response(self, intent: str, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """
        Генерирует AI ответ на основе анализа запроса

        Args:
            intent: Тип запроса
            parameters: Параметры запроса
            context: Контекст разговора

        Returns:
            str: Сгенерированный ответ
        """
        try:
            if intent == 'greeting':
                return ("👋 Здравствуйте! Я AI консультант по клубам и сообществам.\n\n"
                       "Я могу помочь вам:\n"
                       "🔍 Найти интересные клубы по вашим интересам\n"
                       "🏢 Получить информацию о конкретных клубах\n"
                       "🎯 Получить персонализированные рекомендации\n"
                       "💡 Рассказать о создании собственного клуба\n\n"
                       "Чем могу помочь?")

            elif intent == 'club_creation':
                return self._generate_club_creation_response(parameters)

            elif intent == 'club_search':
                return self._generate_club_search_response(parameters)

            elif intent == 'club_info':
                return self._generate_club_info_response(parameters)

            else:
                # Для общих запросов используем RAG
                query = " ".join(parameters.values()) if parameters else "общий запрос"
                return self.rag_service.query(query)

        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return ("Извините, произошла ошибка при обработке вашего запроса. "
                   "Пожалуйста, попробуйте задать вопрос по-другому.")

    def _generate_club_creation_response(self, parameters: Dict[str, Any]) -> str:
        """Генерирует ответ по созданию клуба"""
        response_parts = [
            "🎉 Отличная идея! Создание клуба - это замечательно!\n\n"
        ]

        if 'club_name' in parameters:
            response_parts.append(f"📝 Вы хотите создать клуб: *{parameters['club_name']}*")

        if 'interests' in parameters:
            response_parts.append(f"🎯 Интересы: {', '.join(parameters['interests'])}")

        response_parts.extend([
            "\n📋 Для создания клуба вам нужно:",
            "1. Перейти в раздел *\"Создавайте сообщества\"*",
            "2. Заполнить форму с информацией о клубе:",
            "   • Название клуба",
            "   • Категория",
            "   • Описание (минимум 200 символов)",
            "   • Контактная информация",
            "   • Город",
            "   • Фотографии",
            "3. Добавить теги для лучшего поиска",
            "4. Указать целевую аудиторию",
            "5. Описать мероприятия клуба",
            "\n💡 *Советы для успешного клуба:*",
            "• Придумайте запоминающееся название",
            "• Сделайте качественное описание",
            "• Добавьте несколько фотографий",
            "• Укажите регулярные мероприятия",
            "• Будьте активны в общении с участниками"
        ])

        response_parts.append(
            f"\n🔗 *Ссылка для создания:* {settings.HOSTNAME}/clubs/create/"
        )

        return "\n".join(response_parts)

    def _generate_club_search_response(self, parameters: Dict[str, Any]) -> str:
        """Генерирует ответ по поиску клубов"""
        limit = parameters.get('limit', 5)

        # Поиск клубов
        clubs = self.search_clubs(parameters, limit)

        if not clubs:
            return ("😔 К сожалению, по вашим критериям не найдено подходящих клубов.\n\n"
                   "💡 *Попробуйте:*"
                   "• Расширить географию поиска"
                   "• Уточнить интересы"
                   "• Использовать более общие запросы"
                   "\n🎯 *Или получите персонализированные рекомендации:*"
                   "Напишите мне о своих интересах, и я подберу最适合ные клубы!")

        response_parts = [
            f"🔍 *Найдено {len(clubs)} клубов по вашему запросу:*\n"
        ]

        for i, club in enumerate(clubs, 1):
            response_parts.append(
                f"{i}. 🏆 *{club.name}*\n"
                f"   📂 {club.category.name}\n"
                f"   📍 {club.city.name if club.city else 'Не указан'}\n"
                f"   👥 {club.members_count} участников\n"
                f"   💬 {club.description[:100]}{'...' if len(club.description) > 100 else ''}"
            )

            if club.is_featured:
                response_parts[-1] += " 🌟"

            response_parts.append("")

        response_parts.append(f"\n🔗 *Перейти к поиску:* {settings.HOSTNAME}/clubs/")

        return "\n".join(response_parts)

    def _generate_club_info_response(self, parameters: Dict[str, Any]) -> str:
        """Генерирует ответ с информацией о конкретном клубе"""
        if 'club_name' not in parameters:
            return ("Пожалуйста, уточните название клуба, о котором хотите узнать.\n"
                   "Например: \"Расскажи о клубе [название клуба]\"")

        club = self.get_club_info(parameters['club_name'])

        if not club:
            return ("😔 Клуб с таким названием не найден.\n\n"
                   "💡 *Попробуйте:*"
                   "• Проверить правильность написания названия"
                   "• Перейти в раздел поиска клубов"
                   "• Задать более общий запрос")

        return self.format_club_info(club)

    def process_user_message(self, message: str, session_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Обрабатывает сообщение пользователя и возвращает ответ

        Args:
            message: Сообщение от пользователя
            session_data: Данные сессии (опционально)

        Returns:
            Dict: Результат с ответом и метаданными
        """
        # Анализируем запрос
        analysis = self.analyze_user_query(message)

        # Генерируем ответ
        response = self.generate_ai_response(
            analysis['intent'],
            analysis['parameters'],
            session_data
        )

        return {
            'response': response,
            'intent': analysis['intent'],
            'parameters': analysis['parameters'],
            'timestamp': timezone.now().isoformat()
        }