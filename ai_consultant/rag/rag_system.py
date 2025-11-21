"""
🔍 RAG (Retrieval-Augmented Generation) система для ИИ-консультанта
Обеспечивает актуальную информацию из базы знаний в реальном времени
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from django.core.cache import cache
from django.conf import settings
import json
import re
from datetime import datetime, timedelta

from ..knowledge.platform_knowledge_base import platform_knowledge

logger = logging.getLogger(__name__)


class RAGSystem:
    """
    Система извлечения и обогащения информации для ИИ-агентов
    """

    def __init__(self):
        self.cache_timeout = getattr(settings, 'RAG_CACHE_TIMEOUT', 3600)  # 1 час
        self.similarity_threshold = 0.3

    # =====================================================
    # ОСНОВНЫЕ ФУНКЦИИ RAG
    # =====================================================

    def get_relevant_context(self, query: str, agent_type: str = "orchestrator",
                           user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Получить релевантный контекст для запроса

        Args:
            query: Запрос пользователя
            agent_type: Тип агента
            user_context: Дополнительный контекст пользователя

        Returns:
            Dict с релевантной информацией
        """
        try:
            # 1. Нормализация запроса
            normalized_query = self._normalize_query(query)

            # 2. Определение намерения
            intent = self._classify_intent(normalized_query)

            # 3. Поиск релевантной информации
            context_data = self._retrieve_relevant_info(normalized_query, intent, agent_type)

            # 4. Обогащение контекстом пользователя
            if user_context:
                context_data.update(self._enrich_with_user_context(user_context, agent_type))

            # 5. Генерация форматированного контекста
            formatted_context = self._format_context_for_agent(context_data, agent_type)

            # 6. Кэширование результата
            cache_key = f"rag_context_{hash(query)}_{agent_type}"
            cache.set(cache_key, formatted_context, self.cache_timeout)

            return {
                "success": True,
                "context": formatted_context,
                "intent": intent,
                "sources": context_data.get("sources", []),
                "query_analysis": {
                    "original": query,
                    "normalized": normalized_query,
                    "keywords": self._extract_keywords(normalized_query)
                }
            }

        except Exception as e:
            logger.error(f"RAG system error: {e}", exc_info=True)
            return self._get_fallback_context(query, agent_type)

    # =====================================================
    # АНАЛИЗ И КЛАССИФИКАЦИЯ ЗАПРОСОВ
    # =====================================================

    def _normalize_query(self, query: str) -> str:
        """Нормализация запроса для анализа"""
        # Приведение к нижнему регистру
        normalized = query.lower().strip()

        # Удаление лишних пробелов
        normalized = re.sub(r'\s+', ' ', normalized)

        # Удаление пунктуации (кроме важных символов)
        normalized = re.sub(r'[^\w\s\?\!]', ' ', normalized)

        # Расширение сокращений
        expansions = {
            'ит': 'информационные технологии',
            'айти': 'информационные технологии',
            'смм': 'социальные медиа маркетинг',
            'pr': 'паблик рилейшнз',
            'hr': 'хьюман ресурс',
            'сео': 'поисковая оптимизация'
        }

        for abbr, expansion in expansions.items():
            normalized = normalized.replace(abbr, expansion)

        return normalized.strip()

    def _classify_intent(self, query: str) -> Dict[str, Any]:
        """Классификация намерения пользователя"""
        intent_patterns = {
            "club_creation": {
                "keywords": ["создать", "создай", "хочу создать", "создание", "новый клуб", "создам"],
                "weight": 0.8
            },
            "club_search": {
                "keywords": ["найди", "найти", "поиск", "ищу", "какой", "какие есть", "покажи"],
                "weight": 0.7
            },
            "join_club": {
                "keywords": ["вступить", "вступлю", "как вступить", "хочу вступить", "присоединиться"],
                "weight": 0.6
            },
            "learning": {
                "keywords": ["научиться", "изучить", "обучение", "курс", "развиваться", "навык"],
                "weight": 0.7
            },
            "technical_help": {
                "keywords": ["помощь", "проблема", "не работает", "ошибка", "вопрос", "как"],
                "weight": 0.6
            },
            "general_info": {
                "keywords": ["что такое", "расскажи", "информация", "о платформе", "что это"],
                "weight": 0.5
            }
        }

        query_words = set(query.split())
        intent_scores = {}

        for intent_name, intent_data in intent_patterns.items():
            keywords = set(intent_data["keywords"])
            overlap = len(query_words & keywords)
            score = overlap / len(keywords) * intent_data["weight"]
            intent_scores[intent_name] = score

        # Определение основного намерения
        primary_intent = max(intent_scores.items(), key=lambda x: x[1])

        return {
            "primary_intent": primary_intent[0] if primary_intent[1] > 0 else "general",
            "confidence": primary_intent[1],
            "all_scores": intent_scores
        }

    def _extract_keywords(self, query: str) -> List[str]:
        """Извлечение ключевых слов из запроса"""
        # Убираем стоп-слова
        stop_words = {
            'и', 'в', 'на', 'с', 'по', 'для', 'о', 'об', 'от', 'к', 'у', 'из', 'за',
            'что', 'как', 'где', 'когда', 'почему', 'зачем', 'какой', 'какая', 'какие',
            'я', 'ты', 'он', 'она', 'они', 'мы', 'вы', 'меня', 'тебя', 'его', 'ее',
            'этот', 'тот', 'это', 'тот', 'такой', 'такая', 'такие', 'здесь', 'там',
            'хочу', 'могу', 'надо', 'нужно', 'буду', 'будет', 'есть', 'быть', 'был'
        }

        words = query.split()
        keywords = [word for word in words if word not in stop_words and len(word) > 2]

        # Ищем названия категорий
        categories = ["спорт", "хобби", "профессия", "творчество", "бизнес", "it", "технологии"]
        for category in categories:
            if category in query:
                keywords.append(category)

        return list(set(keywords))

    # =====================================================
    # ПОИСК РЕЛЕВАНТНОЙ ИНФОРМАЦИИ
    # =====================================================

    def _retrieve_relevant_info(self, query: str, intent: Dict[str, Any],
                              agent_type: str) -> Dict[str, Any]:
        """Поиск релевантной информации в базе знаний"""
        context = {}
        sources = []

        # 1. Базовая информация о платформе
        if intent["primary_intent"] in ["general_info", "technical_help"]:
            context["platform_info"] = platform_knowledge.PLATFORM_INFO
            sources.append("platform_knowledge_base")

        # 2. Информация о категориях
        categories_keywords = ["спорт", "хобби", "профессия", "категории"]
        if any(keyword in query for keyword in categories_keywords):
            context["categories"] = platform_knowledge.CATEGORIES
            sources.append("categories_database")

        # 3. Инструкции
        if intent["primary_intent"] == "club_creation":
            context["create_club_instruction"] = platform_knowledge.get_instruction("create_club")
            sources.append("instructions_database")

        if intent["primary_intent"] == "join_club":
            context["join_club_instruction"] = platform_knowledge.get_instruction("join_club")
            sources.append("instructions_database")

        # 4. Функционал платформы
        features_keywords = ["мероприятие", "услуга", "партнерство", "поиск", "объявление"]
        if any(keyword in query for keyword in features_keywords):
            context["platform_features"] = platform_knowledge.PLATFORM_FEATURES
            sources.append("features_database")

        # 5. Ценности и преимущества
        if intent["primary_intent"] in ["general_info", "club_search"]:
            context["value_propositions"] = platform_knowledge.VALUE_PROPOSITIONS
            sources.append("value_propositions")

        # 6. Стили общения для агента
        context["communication_style"] = platform_knowledge.get_communication_style(agent_type)

        # 7. Ключевые фразы
        context["key_phrases"] = platform_knowledge.KEY_PHRASES

        # 8. Истории успеха (для мотивации)
        if intent["primary_intent"] in ["general_info", "learning"]:
            context["success_stories"] = platform_knowledge.SUCCESS_STORIES[:2]  # Первые 2 истории
            sources.append("success_stories")

        # 9. Частые вопросы
        if intent["primary_intent"] == "technical_help":
            context["faq"] = platform_knowledge.FAQ
            sources.append("faq_database")

        context["sources"] = sources
        return context

    def _enrich_with_user_context(self, user_context: Dict[str, Any],
                                 agent_type: str) -> Dict[str, Any]:
        """Обогащение контекста данными пользователя"""
        enriched = {}

        # Геолокация
        if user_context.get("city"):
            enriched["user_city"] = user_context["city"]
            enriched["local_recommendations"] = self._get_local_recommendations(user_context["city"])

        # Интересы
        if user_context.get("interests"):
            interests = user_context["interests"]
            enriched["personalized_categories"] = self._map_interests_to_categories(interests)

        # История взаимодействия
        if user_context.get("interaction_history"):
            enriched="conversation_context" = self._analyze_conversation_history(
                user_context["interaction_history"]
            )

        # Уровень пользователя
        if user_context.get("skill_level"):
            enriched["adaptation_level"] = user_context["skill_level"]

        return enriched

    # =====================================================
    # ФОРМАТИРОВАНИЕ КОНТЕКСТА ДЛЯ АГЕНТОВ
    # =====================================================

    def _format_context_for_agent(self, context_data: Dict[str, Any],
                                agent_type: str) -> str:
        """Форматирование контекента для конкретного типа агента"""
        formatted_sections = []

        # Базовая информация (для всех агентов)
        if "platform_info" in context_data:
            info = context_data["platform_info"]
            formatted_sections.append(
                f"🏢 **ПЛАТФОРМА:** {info['name']} ({info['country']})\n"
                f"📋 **МИССИЯ:** {info['mission']}\n"
                f"🎯 **СЛОГАН:** {info['main_slogan']}"
            )

        # Информация о категориях
        if "categories" in context_data:
            formatted_sections.append("\n🏷️ **КАТЕГОРИИ КЛУБОВ:**")
            for cat_key, cat_data in context_data["categories"].items():
                formatted_sections.append(
                    f"{cat_data['emoji']} **{cat_data['name']}** - {cat_data['description']}\n"
                    f"   Примеры: {', '.join(cat_data['examples'][:3])}..."
                )

        # Инструкции (для поддержки и создания)
        if "create_club_instruction" in context_data:
            instruction = context_data["create_club_instruction"]
            formatted_sections.append(
                f"\n📝 **ИНСТРУКЦИЯ СОЗДАНИЯ КЛУБА:**\n"
                f"Обязательные поля: {', '.join([f['name'] for f in instruction['required_fields']])}"
            )

        # Ценности (для мотивации)
        if "value_propositions" in context_data:
            props = context_data["value_propositions"]
            formatted_sections.append(
                f"\n✨ **ЦЕННОСТИ ПЛАТФОРМЫ:**\n" +
                "\n".join(f"• {benefit}" for benefit in props['main_benefits'][:3])
            )

        # Истории успеха (для вдохновения)
        if "success_stories" in context_data:
            formatted_sections.append("\n🌟 **ИСТОРИИ УСПЕХА:**")
            for story in context_data["success_stories"]:
                formatted_sections.append(f"• {story['title']}")

        # Стиль общения
        if "communication_style" in context_data:
            style = context_data["communication_style"]
            formatted_sections.append(
                f"\n🎭 **СТИЛЬ ОБЩЕНИЯ:**\n"
                f"• Тон: {style['style']}\n"
                f"• Обращение: на '{style['address']}'\n"
                f"• Подход: {style['approach']}"
            )

        # Локализация
        if "user_city" in context_data:
            formatted_sections.append(
                f"\n📍 **ЛОКАЛИЗАЦИЯ:** Пользователь из города {context_data['user_city']}"
            )

        # Персонализация
        if "personalized_categories" in context_data:
            cats = context_data["personalized_categories"]
            formatted_sections.append(
                f"\n🎯 **РЕКОМЕНДОВАННЫЕ КАТЕГОРИИ:** {', '.join(cats)}"
            )

        return "\n".join(formatted_sections)

    # =====================================================
    # ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
    # =====================================================

    def _get_local_recommendations(self, city: str) -> List[str]:
        """Получить локальные рекомендации"""
        # Здесь может быть подключение к реальной базе данных
        # Пока используем моковые данные
        local_cache = {
            "алматы": ["Горные клубы", "IT-сообщества", "Творческие студии"],
            "астана": ["Государственные клубы", "Бизнес сообщества", "Спортивные федерации"],
            "шымкент": ["Культурные сообщества", "Традиционные клубы", "Семейные объединения"]
        }
        return local_cache.get(city.lower(), ["Региональные сообщества"])

    def _map_interests_to_categories(self, interests: List[str]) -> List[str]:
        """Отобразить интересы на категории платформы"""
        category_mapping = {
            "программирование": "Профессия",
            "спорт": "Спорт",
            "творчество": "Хобби",
            "бизнес": "Профессия",
            "искусство": "Хобби",
            "фитнес": "Спорт",
            "маркетинг": "Профессия",
            "музыка": "Хобби"
        }

        categories = []
        for interest in interests:
            category = category_mapping.get(interest.lower())
            if category and category not in categories:
                categories.append(category)

        return categories or ["Все категории"]

    def _analyze_conversation_history(self, history: List[Dict]) -> Dict[str, Any]:
        """Анализ истории разговора"""
        if not history:
            return {}

        # Анализ последних сообщений
        recent_messages = history[-5:]  # Последние 5 сообщений

        # Определение тем
        topics = []
        for msg in recent_messages:
            if "клуб" in msg.get("content", "").lower():
                topics.append("club_interest")
            if "создать" in msg.get("content", "").lower():
                topics.append("creation_intent")

        return {
            "detected_topics": topics,
            "message_count": len(history),
            "last_interaction": max(msg.get("timestamp", "") for msg in recent_messages)
        }

    def _get_fallback_context(self, query: str, agent_type: str) -> Dict[str, Any]:
        """Резервный контекст при ошибках"""
        return {
            "success": False,
            "context": f"🤖 ИИ-консультант платформы 'ЦЕНТР СОБЫТИЙ'.\nРаботаю в режиме ограниченной функциональности.",
            "intent": {"primary_intent": "general", "confidence": 0.5},
            "sources": ["fallback"],
            "error": "RAG system temporarily unavailable"
        }

    # =====================================================
    # УПРАВЛЕНИЕ КАЧЕСТВОМ
    # =====================================================

    def validate_context_quality(self, context: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Валидация качества контекста"""
        validation_score = 0
        max_score = 100
        issues = []

        # Проверка наличия базовой информации
        if "platform_info" in context.get("context", ""):
            validation_score += 20
        else:
            issues.append("Отсутствует базовая информация о платформе")

        # Проверка релевантности
        query_words = set(query.lower().split())
        context_words = set(context.get("context", "").lower().split())
        relevance = len(query_words & context_words) / max(len(query_words), 1)
        validation_score += min(relevance * 30, 30)

        if relevance < 0.3:
            issues.append("Низкая релевантность контекста запросу")

        # Проверка структурированности
        if "🏢" in context.get("context", ""):
            validation_score += 20
        else:
            issues.append("Контекст не структурирован")

        # Проверка адаптации под агента
        if "🎭" in context.get("context", ""):
            validation_score += 15
        else:
            issues.append("Нет адаптации под тип агента")

        # Проверка полноты
        context_length = len(context.get("context", ""))
        if context_length > 200:
            validation_score += 15
        else:
            issues.append("Контекст слишком короткий")

        return {
            "validation_score": validation_score,
            "max_score": max_score,
            "quality_level": "excellent" if validation_score >= 90 else
                            "good" if validation_score >= 75 else
                            "satisfactory" if validation_score >= 60 else "poor",
            "issues": issues,
            "recommendations": self._get_context_recommendations(validation_score, issues)
        }

    def _get_context_recommendations(self, score: float, issues: List[str]) -> List[str]:
        """Получить рекомендации по улучшению контекста"""
        recommendations = []

        if score < 75:
            recommendations.append("🔍 Улучшить поиск релевантной информации")

        if "Низкая релевантность" in "".join(issues):
            recommendations.append("🎯 Улучшить классификацию намерений")

        if "Отсутствует базовая информация" in issues:
            recommendations.append("📋 Добавить базовую информацию о платформе")

        if "Контекст не структурирован" in issues:
            recommendations.append("📝 Улучшить форматирование контекста")

        return recommendations or ["✅ Контекст высокого качества"]


# Глобальный экземпляр RAG системы
rag_system = RAGSystem()