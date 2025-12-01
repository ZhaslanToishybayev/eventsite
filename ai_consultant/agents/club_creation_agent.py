"""
🤖 Advanced Club Creation AI Agent
Интеллектуальный агент для создания клубов через естественный диалог
"""

import json
import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import asyncio

from django.conf import settings
from django.core.cache import cache
from django.contrib.auth.models import User
from django.utils import timezone

# NLP and AI
import openai
from sentence_transformers import SentenceTransformer
from transformers import pipeline

# Django models
from clubs.models import Club, ClubCategory, UserInterest, UserInteraction

# Enhanced AI components
from ai_consultant.rag.enhanced_rag_service import get_enhanced_rag_service
from ai_consultant.recommendations.recommendation_engine import get_recommendation_engine
from ai_consultant.knowledge.platform_knowledge_base import platform_knowledge

logger = logging.getLogger(__name__)


class ClubCreationAgent:
    """
    🤖 ИИ-агент для создания клубов через диалог
    Ведет естественный разговор и помогает пользователю создать клуб
    """

    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

        # Enhanced AI components
        self.rag_service = get_enhanced_rag_service()
        self.recommendation_engine = get_recommendation_engine()

        # Состояние диалога
        self.conversation_states = {}

        # Этапы создания клуба
        self.creation_stages = [
            'greeting',
            'idea_discovery',
            'category_selection',
            'name_creation',
            'description_writing',
            'details_collection',
            'review',
            'confirmation'
        ]

        # Расширенные состояния для сложных сценариев
        self.complex_idea_states = {
            'multi_category': 'Многопрофильные клубы',
            'hybrid_format': 'Гибридные форматы (онлайн + офлайн)',
            'special_interest': 'Специальные интересы',
            'social_cause': 'Социальные и благотворительные клубы'
        }

        # Кэш для оптимизации
        self.category_cache = {}
        self.validation_cache = {}
        self.name_generation_cache = {}

        # Настраиваемые параметры
        self.max_session_duration = 30  # минут
        self.suggestion_count = 5
        self.max_name_suggestions = 8
        self.max_description_suggestions = 3

        # Advanced NLU components
        self.intent_classifier = pipeline("text-classification",
                                        model="distilbert-base-uncased-finetuned-sst-2-english",
                                        return_all_scores=True)
        self.ner_pipeline = pipeline("ner", model="dbmdz/bert-large-cased-finetuned-conll03-english")

        logger.info("🤖 Enhanced Club Creation Agent initialized with RAG and advanced NLU")

    async def process_user_message(self, user_id: int, message: str,
                                 context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Обработка сообщения пользователя и генерация ответа агента
        """
        try:
            # Получаем или создаем состояние диалога
            session = self._get_or_create_session(user_id)
            session['last_activity'] = timezone.now()

            # Анализируем сообщение
            message_analysis = await self._analyze_message(message, session)

            # Сохраняем анализ в сессию для использования в генерации ответа
            session['current_analysis'] = message_analysis

            session['message_history'].append({
                'message': message,
                'analysis': message_analysis,
                'timestamp': timezone.now().isoformat()
            })

            # Определяем следующее действие
            next_action = await self._determine_next_action(message_analysis, session)
            session['current_action'] = next_action

            # Генерируем ответ
            response = await self._generate_agent_response(next_action, session, context)

            # Обновляем состояние
            self._update_session(user_id, session)

            # Проверяем завершение создания
            if session.get('club_creation_complete'):
                await self._finalize_club_creation(user_id, session)

            return {
                'success': True,
                'response': response,
                'session_state': session['current_stage'],
                'next_steps': self._get_next_steps(session),
                'suggestions': session.get('suggestions', []),
                'progress': self._calculate_progress(session)
            }

        except Exception as e:
            logger.error(f"❌ Error in club creation agent: {e}", exc_info=True)
            return {
                'success': False,
                'response': await self._generate_error_response(),
                'session_state': 'error'
            }

    def _get_or_create_session(self, user_id: int) -> Dict[str, Any]:
        """Получаем или создаем сессию пользователя"""
        cache_key = f"club_creation_session_{user_id}"
        session = cache.get(cache_key)

        if not session:
            session = {
                'user_id': user_id,
                'start_time': timezone.now(),
                'current_stage': 'greeting',
                'current_action': 'greet_user',
                'message_history': [],
                'club_data': {},
                'suggestions': [],
                'completed_stages': [],
                'current_step_data': {}
            }
            cache.set(cache_key, session, 3600)  # 1 час

        self.conversation_states[user_id] = session
        return session

    async def _analyze_message(self, message: str, session: Dict[str, Any]) -> Dict[str, Any]:
        """
        🧠 Расширенный анализ сообщения пользователя с использованием RAG и NLU
        """
        try:
            # 1. Advanced intent analysis using OpenAI
            analysis_prompt = f"""
            Проанализируй сообщение пользователя для создания клуба:

            Сообщение: "{message}"

            Определи:
            1. Намерение (intent): [club_creation, category_question, name_idea, description_help, details_info, ready_to_create, small_talk, complex_idea, multi_category, social_cause]
            2. Категория интересов (category): [спорт, хобби, профессия, it, технологии, бизнес, искусство, образование, здоровье, другие, благотворительность, социальные, многопрофильный]
            3. Конкретная идея (club_idea): краткое описание идеи клуба
            4. Готовность к созданию (readiness): [низкая, средняя, высокая, очень высокая]
            5. Эмоциональный тон (tone): [восторженный, сомневающийся, деловой, дружелюбный, неуверенный, вдохновленный]
            6. Сложность идеи (complexity): [простая, средняя, сложная, очень сложная]
            7. Особые требования (special_requirements): [онлайн, офлайн, гибрид, благотворительность, образовательная, профессиональная]

            Учти:
            - Если пользователь упоминает несколько интересов, это может быть многопрофильный клуб
            - Если есть упоминание о помощи, благотворительности - это социальный клуб
            - Если есть технические термины - это может быть профессиональный/IT клуб

            Верни JSON с анализом.
            """

            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-4",
                messages=[{"role": "user", "content": analysis_prompt}],
                max_tokens=500,
                temperature=0.3
            )

            analysis_text = response.choices[0].message.content
            analysis = json.loads(analysis_text)

            # 2. Extract entities using NER
            try:
                entities = self.ner_pipeline(message)
                analysis['entities'] = entities
            except Exception as e:
                logger.warning(f"NER analysis failed: {e}")
                analysis['entities'] = []

            # 3. Semantic similarity search using RAG
            try:
                rag_results = await self.rag_service.semantic_search(
                    query=message,
                    collections=['clubs', 'categories', 'platform_info'],
                    top_k=5
                )
                analysis['rag_context'] = rag_results
            except Exception as e:
                logger.warning(f"RAG search failed: {e}")
                analysis['rag_context'] = []

            # 4. Advanced complexity analysis
            complexity_score = self._calculate_complexity_score(message, analysis)
            analysis['complexity_score'] = complexity_score

            # 5. Personalization based on user context
            user_context = session.get('user_context', {})
            if user_context:
                analysis['personalized_suggestions'] = await self._get_personalized_suggestions(
                    analysis, user_context
                )

            return analysis

        except Exception as e:
            logger.error(f"❌ Error in advanced message analysis: {e}")
            return {
                'intent': 'club_creation',
                'category': 'other',
                'club_idea': message[:100],
                'readiness': 'средняя',
                'tone': 'дружелюбный',
                'complexity': 'средняя',
                'entities': [],
                'rag_context': [],
                'complexity_score': 0.5
            }

    async def _determine_next_action(self, analysis: Dict[str, Any],
                                   session: Dict[str, Any]) -> str:
        """Определяем следующее действие агента"""
        current_stage = session['current_stage']
        intent = analysis.get('intent', 'club_creation')
        readiness = analysis.get('readiness', 'низкая')

        # Если пользователь явно хочет создать клуб
        if intent == 'ready_to_create':
            return 'collect_club_details'

        # Логика перехода между этапами
        stage_actions = {
            'greeting': 'greet_user',
            'idea_discovery': 'explore_club_idea',
            'category_selection': 'suggest_categories',
            'name_creation': 'help_with_name',
            'description_writing': 'help_with_description',
            'details_collection': 'collect_details',
            'review': 'review_club',
            'confirmation': 'confirm_creation'
        }

        # Проверяем завершение текущего этапа
        if await self._is_stage_complete(current_stage, analysis, session):
            next_stage_index = self.creation_stages.index(current_stage) + 1
            if next_stage_index < len(self.creation_stages):
                next_stage = self.creation_stages[next_stage_index]
                session['current_stage'] = next_stage
                return stage_actions.get(next_stage, 'greet_user')

        return stage_actions.get(current_stage, 'greet_user')

    async def _is_stage_complete(self, stage: str, analysis: Dict[str, Any],
                                session: Dict[str, Any]) -> bool:
        """Проверяем завершение этапа"""
        club_data = session.get('club_data', {})

        if stage == 'idea_discovery':
            return bool(club_data.get('main_idea') or analysis.get('club_idea'))
        elif stage == 'category_selection':
            return bool(club_data.get('category'))
        elif stage == 'name_creation':
            return bool(club_data.get('name'))
        elif stage == 'description_writing':
            return bool(club_data.get('description'))
        elif stage == 'details_collection':
            required_fields = ['email', 'phone', 'city']
            return all(club_data.get(field) for field in required_fields)

        return False

    async def _generate_agent_response(self, action: str, session: Dict[str, Any],
                                     context: Dict[str, Any]) -> str:
        """Генерируем ответ агента"""
        try:
            # Формируем контекст для генерации
            prompt = await self._build_response_prompt(action, session, context)

            # Определяем сложность запроса для выбора модели
            analysis = session.get('current_analysis', {})
            complexity_score = analysis.get('complexity_score', 0.5)

            # Используем GPT-4 для сложных случаев и специальных запросов
            if (complexity_score > 0.7 or
                action in ['help_with_name', 'help_with_description'] or
                analysis.get('intent') in ['complex_idea', 'multi_category', 'social_cause']):
                model = "gpt-4"
                max_tokens = 800
                temperature = 0.7
            else:
                model = "gpt-3.5-turbo"
                max_tokens = 500
                temperature = 0.7

            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model=model,
                messages=[
                    {"role": "system", "content": self._get_agent_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"❌ Error generating agent response: {e}")
            return "Извините, произошла ошибка. Давайте начнем сначала?"

    def _build_response_prompt(self, action: str, session: Dict[str, Any],
                             context: Dict[str, Any]) -> str:
        """Строим промпт для генерации ответа"""
        club_data = session.get('club_data', {})
        message_history = session.get('message_history', [])

        base_prompt = f"""
        Ты - ИИ-агент по созданию клубов на платформе UnitySphere.
        Твоя задача - помочь пользователю создать клуб через естественный диалог.

        Текущий этап: {session['current_stage']}
        Действие: {action}

        Данные о клубе: {json.dumps(club_data, ensure_ascii=False, indent=2)}

        История сообщений: {json.dumps(message_history[-3:], ensure_ascii=False, indent=2)}

        Контекст пользователя: {json.dumps(context, ensure_ascii=False, indent=2)}

        """

        action_prompts = {
            'greet_user': self._build_greeting_prompt(base_prompt, context),
            'explore_club_idea': self._build_idea_prompt(base_prompt, club_data),
            'suggest_categories': self._build_category_prompt(base_prompt, club_data),
            'help_with_name': self._build_name_prompt(base_prompt, club_data),
            'help_with_description': self._build_description_prompt(base_prompt, club_data),
            'collect_details': self._build_details_prompt(base_prompt, club_data),
            'review_club': self._build_review_prompt(base_prompt, club_data),
            'confirm_creation': self._build_confirmation_prompt(base_prompt, club_data)
        }

        return action_prompts.get(action, base_prompt)

    def _build_greeting_prompt(self, base: str, context: Dict[str, Any]) -> str:
        """Промпт для приветствия"""
        interests = context.get('interests', [])
        city = context.get('city', 'вашем городе')

        return base + f"""
        Поприветствуй пользователя и предложи помощь в создании клуба.
        Упомяни интересы пользователя: {', '.join(interests) if interests else 'различные интересы'}
        и возможность создать клуб в {city}.

        Сделай приветствие дружелюбным и вдохновляющим.
        Предложи начать с обсуждения идеи клуба.
        """

    def _build_idea_prompt(self, base: str, club_data: Dict[str, Any]) -> str:
        """Промпт для обсуждения идеи"""
        return base + f"""
        Обсуди с пользователем идею для клуба.
        Задай вопросы:
        1. Что именно вы хотите создать?
        2. Для кого этот клуб?
        3. Какие цели у клуба?
        4. Что будет происходить на встречах?

        Предложи уточнения и помоги сформулировать четкую идею.
        """

    def _build_category_prompt(self, base: str, club_data: Dict[str, Any]) -> str:
        """Промпт для выбора категории"""
        club_idea = club_data.get('main_idea', '')
        context = club_data.get('context', {})

        # Используем recommendation engine для получения персонализированных категорий
        personalized_categories = self._get_personalized_categories(club_idea, context)

        return base + f"""
        🔍 Помоги пользователю выбрать категорию для клуба.

        Идея клуба: {club_idea}

        🎯 Персонализированные предложения на основе анализа:
        {self._format_categories_list(personalized_categories)}

        📊 Другие популярные категории:
        • Спорт и ЗОЖ (фитнес, командные игры, единоборства, активный отдых)
        • Хобби и творчество (рукоделие, игры, искусство, музыка, фотография)
        • Профессия и развитие (бизнес, IT, образование, карьерный рост)
        • Технологии и инновации (программирование, гаджеты, робототехника)
        • Социальные инициативы (благотворительность, волонтерство, экология)
        • Образ жизни (путешествия, кулинария, здоровье, семьи)
        • Развлечения (кино, книги, настольные игры, квесты)

        💡 Критерии выбора категории:
        1. Какая категория лучше всего отражает суть вашего клуба?
        2. Какая категория привлечет вашу целевую аудиторию?
        3. Есть ли уже похожие клубы в этой категории?
        4. Какая категория имеет наибольший потенциал роста?

        🤔 Задайте пользователю вопросы:
        - Какие другие интересы может объединять ваш клуб?
        - Планируете ли вы расширять деятельность в будущем?
        - Есть ли предпочтения по аудитории?
        - Хотите ли выбрать узкую или широкую категорию?

        📈 Также предложите:
        - Анализ конкурентов в выбранной категории
        - Рекомендации по позиционированию
        - Идеи для уникального предложения
        """

    def _build_name_prompt(self, base: str, club_data: Dict[str, Any]) -> str:
        """Промпт для придумывания названия"""
        idea = club_data.get('main_idea', '')
        category = club_data.get('category', '')
        return base + f"""
        🏷️ Помоги придумать креативные названия для клуба.

        Идея: {idea}
        Категория: {category}

        🎯 Требования к названиям:
        1. Запоминающиеся и легко произносимые
        2. Отражают суть и миссию клуба
        3. Подходящие для казахстанской аудитории
        4. Уникальные и нестандартные
        5. Могут быть на русском, казахском или английском языке

        📋 Сгенерируй 8 вариантов названий в следующих стилях:
        • Описательные (четко отражающие суть)
        • Метафорические (символические, образные)
        • Аббревиатуры (составные из ключевых слов)
        • Сленговые (молодежные, современные)
        • Классические (традиционные, устоявшиеся)
        • Инновационные (современные, технологичные)
        • Локализованные (с учетом казахстанской специфики)
        • Уникальные (необычные, креативные)

        💡 Для каждого названия укажи:
        - Стиль названия
        - Почему оно подходит
        - Какие эмоции вызывает
        - Легко ли запоминается

        🤔 Также задай пользователю вопросы о предпочтениях:
        - Какой стиль названия нравится больше?
        - Есть ли предпочтения по языку?
        - Хотите ли что-то классическое или необычное?
        """

    def _build_description_prompt(self, base: str, club_data: Dict[str, Any]) -> str:
        """Промпт для написания описания"""
        name = club_data.get('name', '')
        idea = club_data.get('main_idea', '')
        category = club_data.get('category', '')
        target_audience = club_data.get('target_audience', '')
        activities = club_data.get('activities', '')

        return base + f"""
        📝 Напиши вдохновляющее и подробное описание для клуба.

        Название: {name}
        Идея: {idea}
        Категория: {category}
        Целевая аудитория: {target_audience}
        Активности: {activities}

        🎯 Описание должно включать:
        1. Кто мы и что делаем (2-3 предложения)
        2. Для кого этот клуб (целевая аудитория)
        3. Что происходит на встречах (мероприятия, формат)
        4. Какие ценности и цели
        5. Призыв к действию (присоединяйтесь!)
        6. Что получат участники
        7. Особенности и преимущества

        ✨ Требования к описанию:
        - Вдохновляющим и мотивирующим
        - Конкретным и информативным
        - Дружелюбным и welcoming
        - Профессиональным
        - Не менее 300 слов
        - Используй эмодзи для выделения ключевых моментов

        🏆 Также предложи:
        - 3 варианта краткого слогана (до 10 слов)
        - 5 хештегов для продвижения
        - Идеи для первых 3 мероприятий клуба
        - Советы по привлечению первых участников

        🤔 Задай пользователю вопросы:
        - Как часто планируете встречаться?
        - Онлайн или офлайн формат?
        - Есть ли уже первые идеи мероприятий?
        """

    def _build_details_prompt(self, base: str, club_data: Dict[str, Any]) -> str:
        """Промпт для сбора деталей"""
        return base + f"""
        Собери контактные данные для клуба.

        Запроси по одному:
        1. Email для связи
        2. Телефон для связи
        3. Город/район
        4. Адрес встреч (если есть)
        5. Ссылка на WhatsApp группу (если есть)

        Объясни зачем нужны эти данные.
        Успокой пользователя о конфиденциальности.
        """

    def _build_review_prompt(self, base: str, club_data: Dict[str, Any]) -> str:
        """Промпт для просмотра клуба"""
        return base + f"""
        Покажи пользователю всю информацию о клубе для проверки.

        Данные клуба:
        {json.dumps(club_data, ensure_ascii=False, indent=2)}

        Попроси проверить:
        1. Все ли данные верны
        2. Нужны ли изменения
        3. Готов ли создать клуб

        Предложи внести коррективы если нужно.
        """

    def _build_confirmation_prompt(self, base: str, club_data: Dict[str, Any]) -> str:
        """Промпт для подтверждения создания"""
        return base + f"""
        Подтверди создание клуба.

        Финальная информация:
        {json.dumps(club_data, ensure_ascii=False, indent=2)}

        Объясни что будет дальше:
        1. Клуб будет создан
        2. Начнется модерация (24 часа)
        3. Пользователь получит уведомление
        4. Можно будет редактировать клуб

        Спроси окончательное подтверждение.
        """

    def _get_agent_system_prompt(self) -> str:
        """Системный промпт для агента"""
        return """
        Ты - дружелюбный и профессиональный ИИ-агент по созданию клубов.
        Твоя цель - помочь пользователю создать успешный клуб через естественный диалог.

        Ты должен:
        1. Быть дружелюбным и вдохновляющим
        2. Задавать уточняющие вопросы
        3. Предлагать конкретные идеи и варианты
        4. Объяснять зачем нужны те или иные данные
        5. Поддерживать пользователя на всех этапах
        6. Использовать эмодзи для живости общения
        7. Быть конкретным и полезным
        8. Предлагать следующие шаги

        Не спеши. Проводи пользователя через каждый этап.
        Делай процесс создания клуба увлекательным и познавательным.
        """

    def _get_next_steps(self, session: Dict[str, Any]) -> List[str]:
        """Получаем следующие шаги"""
        current_stage = session['current_stage']
        current_index = self.creation_stages.index(current_stage)

        next_steps = []
        for i in range(current_index, min(current_index + 3, len(self.creation_stages))):
            stage_name = self.creation_stages[i]
            step_descriptions = {
                'greeting': '👋 Поприветствовать пользователя',
                'idea_discovery': '💡 Обсудить идею для клуба',
                'category_selection': '🏷️ Выбрать категорию',
                'name_creation': '📝 Придумать название',
                'description_writing': '✍️ Написать описание',
                'details_collection': '📞 Собрать контактные данные',
                'review': '👀 Проверить все данные',
                'confirmation': '✅ Подтвердить создание'
            }
            next_steps.append(step_descriptions.get(stage_name, stage_name))

        return next_steps

    def _calculate_progress(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Рассчитываем прогресс создания клуба"""
        completed_stages = session.get('completed_stages', [])
        current_stage = session['current_stage']

        total_stages = len(self.creation_stages)
        completed_count = len(completed_stages)

        # Если текущий этап не в списке завершенных, добавляем его как частичный
        if current_stage not in completed_stages:
            completed_count += 0.5

        progress_percent = int((completed_count / total_stages) * 100)

        return {
            'percent': progress_percent,
            'completed': completed_stages,
            'current': current_stage,
            'total': total_stages,
            'remaining': self.creation_stages[len(completed_stages):]
        }

    async def _finalize_club_creation(self, user_id: int, session: Dict[str, Any]):
        """Финализируем создание клуба"""
        try:
            club_data = session['club_data']

            # Создаем клуб в базе данных
            from django.contrib.auth.models import User
            user = User.objects.get(id=user_id)

            club = Club.objects.create(
                name=club_data['name'],
                description=club_data['description'],
                category_id=await self._get_category_id(club_data['category']),
                email=club_data['email'],
                phone=club_data['phone'],
                city=club_data['city'],
                created_by=user,
                is_active=False  # Ожидает модерации
            )

            # Сохраняем сессию как завершенную
            session['club_creation_complete'] = True
            session['club_id'] = club.id

            # Логируем создание
            await self._log_club_creation(user_id, club.id, club_data)

            logger.info(f"✅ Club created successfully: {club.name} (ID: {club.id})")

        except Exception as e:
            logger.error(f"❌ Error finalizing club creation: {e}")

    async def _get_category_id(self, category_name: str) -> Optional[int]:
        """Получаем ID категории"""
        try:
            if category_name in self.category_cache:
                return self.category_cache[category_name]

            category = ClubCategory.objects.filter(
                name__icontains=category_name
            ).first()

            if category:
                self.category_cache[category_name] = category.id
                return category.id

            # Если не найдено, создаем новую категорию
            new_category = ClubCategory.objects.create(
                name=category_name,
                description=f"Категория: {category_name}",
                is_active=True
            )
            self.category_cache[category_name] = new_category.id
            return new_category.id

        except Exception as e:
            logger.error(f"❌ Error getting category ID: {e}")
            return None

    async def _log_club_creation(self, user_id: int, club_id: int, club_data: Dict[str, Any]):
        """Логируем создание клуба"""
        try:
            UserInteraction.objects.create(
                user_id=user_id,
                content=f"Club creation: {club_data.get('name', 'Unknown')}",
                interaction_type='club_creation',
                metadata={
                    'club_id': club_id,
                    'club_data': club_data
                }
            )
        except Exception as e:
            logger.error(f"❌ Error logging club creation: {e}")

    async def _generate_error_response(self) -> str:
        """🚨 Advanced error response with recovery suggestions"""
        import random

        error_templates = [
            """
            Извините, произошла ошибка в работе ассистента по созданию клубов. 🙁

            🔄 **Попробуем восстановиться:**
            1. **Перезапустите диалог** - нажмите кнопку "🔄 Начать сначала"
            2. **Проверьте интернет-соединение** - убедитесь, что соединение стабильно
            3. **Сформулируйте запрос иначе** - возможно, система не поняла ваш запрос

            💡 **Альтернативные варианты:**
            • Создать клуб вручную через [форму создания](/clubs/create/)
            • Обратиться в поддержку через [чат](/support/)
            • Ознакомиться с [инструкцией](/help/club-creation/)

            🤖 **Или просто скажите:** "Начать сначала" и я помогу вам создать клуб!
            """,

            """
            Ой! Похоже, я временно потерял связь с базой знаний. 😅

            🔍 **Что происходит:**
            • Система обрабатывает ваш запрос
            • Возможны временные технические работы
            • Нужно немного времени на восстановление

            ⏳ **Что делать:**
            1. Подождите 1-2 минуты
            2. Нажмите "🔄 Перезапустить"
            3. Попробуйте сформулировать запрос проще

            🚀 **Готовы начать? Просто скажите:** "Хочу создать клуб по [ваш интерес]"
            """,

            """
            Кажется, у нас небольшие технические трудности. Но это не повод останавливаться! 🛠️

            💪 **Варианты решения:**
            • **Мгновенное восстановление:** Нажмите "🔄" для перезапуска диалога
            • **Ручной способ:** Перейдите в [раздел клубов](/clubs/) и создайте вручную
            • **Помощь оператора:** Напишите в [техподдержку](/support/)

            🎯 **Следующие шаги:**
            1. Определитесь с идеей клуба
            2. Выберите подходящую категорию
            3. Придумайте запоминающееся название
            4. Составьте вдохновляющее описание

            Готовы попробовать снова? Просто скажите "Да"! ✨
            """
        ]

        return random.choice(error_templates).strip()

    def _get_personalized_categories(self, club_idea: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        🎯 Получаем персонализированные категории с помощью recommendation engine
        """
        try:
            # Используем recommendation engine для получения персонализированных категорий
            if hasattr(self, 'recommendation_engine') and self.recommendation_engine:
                return self.recommendation_engine.get_category_recommendations(
                    club_idea=club_idea,
                    user_context=context,
                    top_k=3
                )
            else:
                # Резервный вариант
                return self._get_fallback_categories(club_idea)

        except Exception as e:
            logger.error(f"❌ Error getting personalized categories: {e}")
            return self._get_fallback_categories(club_idea)

    def _get_fallback_categories(self, club_idea: str) -> List[Dict[str, Any]]:
        """
        📋 Резервные категории на основе ключевых слов
        """
        categories = []

        # Простой анализ идеи для определения категории
        idea_lower = club_idea.lower()

        if any(word in idea_lower for word in ['спорт', 'фитнес', 'тренировка', 'игра', 'команда']):
            categories.append({
                'name': 'Спорт и ЗОЖ',
                'confidence': 0.9,
                'reason': 'Идея содержит спортивные элементы'
            })

        if any(word in idea_lower for word in ['творчество', 'рисование', 'музыка', 'искусство', 'рукоделие']):
            categories.append({
                'name': 'Хобби и творчество',
                'confidence': 0.9,
                'reason': 'Идея связана с творческой деятельностью'
            })

        if any(word in idea_lower for word in ['работа', 'карьера', 'бизнес', 'профессия', 'образование']):
            categories.append({
                'name': 'Профессия и развитие',
                'confidence': 0.9,
                'reason': 'Идея направлена на профессиональный рост'
            })

        if any(word in idea_lower for word in ['технологии', 'программирование', 'гаджеты', 'роботы', 'ит']):
            categories.append({
                'name': 'Технологии и инновации',
                'confidence': 0.9,
                'reason': 'Идея связана с технологиями'
            })

        if any(word in idea_lower for word in ['помощь', 'благотворительность', 'волонтер', 'социальный']):
            categories.append({
                'name': 'Социальные инициативы',
                'confidence': 0.9,
                'reason': 'Идея имеет социальную направленность'
            })

        # Если не найдено категорий, возвращаем общие
        if not categories:
            categories = [
                {'name': 'Развлечения', 'confidence': 0.5, 'reason': 'Универсальная категория'},
                {'name': 'Образ жизни', 'confidence': 0.5, 'reason': 'Широкая категория'},
                {'name': 'Другие интересы', 'confidence': 0.5, 'reason': 'По умолчанию'}
            ]

        return categories[:3]

    def _format_categories_list(self, categories: List[Dict[str, Any]]) -> str:
        """
        📊 Форматируем список категорий для отображения
        """
        if not categories:
            return "Пока нет персонализированных предложений"

        formatted = []
        for i, category in enumerate(categories, 1):
            confidence_emoji = "⭐⭐⭐" if category['confidence'] >= 0.8 else "⭐⭐" if category['confidence'] >= 0.6 else "⭐"
            formatted.append(f"{i}. **{category['name']}** {confidence_emoji}\n   *{category['reason']}*")

        return "\n".join(formatted)

    def _calculate_complexity_score(self, message: str, analysis: Dict[str, Any]) -> float:
        """
        📊 Рассчитываем сложность идеи клуба
        """
        score = 0.0

        # Анализ длины сообщения
        if len(message) > 200:
            score += 0.2

        # Анализ количества упомянутых интересов
        if 'entities' in analysis:
            entity_count = len(analysis['entities'])
            score += min(entity_count * 0.1, 0.3)

        # Анализ сложности намерения
        intent = analysis.get('intent', '')
        if intent in ['complex_idea', 'multi_category', 'social_cause']:
            score += 0.4

        # Анализ категорий
        category = analysis.get('category', '')
        if category in ['многопрофильный', 'социальные', 'благотворительность']:
            score += 0.3

        return min(score, 1.0)

    async def _get_personalized_suggestions(self, analysis: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        🎯 Генерируем персонализированные предложения на основе контекста пользователя
        """
        try:
            # Используем recommendation engine для персонализированных предложений
            suggestions = await self.recommendation_engine.get_personalized_club_suggestions(
                user_context=user_context,
                analysis=analysis
            )

            return suggestions

        except Exception as e:
            logger.error(f"❌ Error generating personalized suggestions: {e}")
            return {}

    async def _generate_advanced_name_suggestions(self, club_data: Dict[str, Any], analysis: Dict[str, Any]) -> List[str]:
        """
        🏷️ Генерация расширенных предложений названий с использованием GPT-4
        """
        try:
            idea = club_data.get('main_idea', '')
            category = club_data.get('category', '')
            complexity = analysis.get('complexity', 'средняя')

            prompt = f"""
            Придумай креативные названия для клуба на основе следующей информации:

            Идея клуба: {idea}
            Категория: {category}
            Сложность идеи: {complexity}

            Требования к названиям:
            1. Запоминающиеся и легко произносимые
            2. Отражают суть и миссию клуба
            3. Подходящие для казахстанской аудитории
            4. Уникальные и нестандартные
            5. Могут быть на русском, казахском или английском языке

            Сгенерируй 8 вариантов названий в следующих стилях:
            - Описательные (четко отражающие суть)
            - Метафорические (символические, образные)
            - Аббревиатуры (составные из ключевых слов)
            - Сленговые (молодежные, современные)
            - Классические (традиционные, устоявшиеся)
            - Инновационные (современные, технологичные)
            - Локализованные (с учетом казахстанской специфики)
            - Уникальные (необычные, креативные)

            Верни список из 8 названий.
            """

            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.8
            )

            content = response.choices[0].message.content
            names = [line.strip('- ').strip() for line in content.split('\n') if line.strip() and not line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.'))]
            return names[:self.max_name_suggestions]

        except Exception as e:
            logger.error(f"❌ Error generating advanced name suggestions: {e}")
            return self._generate_fallback_names(club_data)

    async def _generate_advanced_description(self, club_data: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """
        📝 Генерация расширенного описания с использованием GPT-4
        """
        try:
            name = club_data.get('name', '')
            idea = club_data.get('main_idea', '')
            category = club_data.get('category', '')
            target_audience = club_data.get('target_audience', '')
            activities = club_data.get('activities', '')

            prompt = f"""
            Напиши вдохновляющее и подробное описание для клуба:

            Название: {name}
            Идея: {idea}
            Категория: {category}
            Целевая аудитория: {target_audience}
            Активности: {activities}

            Описание должно включать:
            1. Кто мы и что делаем (2-3 предложения)
            2. Для кого этот клуб (целевая аудитория)
            3. Что происходит на встречах (мероприятия, формат)
            4. Какие ценности и цели
            5. Призыв к действию (присоединяйтесь!)
            6. Что получат участники
            7. Особенности и преимущества

            Сделай описание:
            - Вдохновляющим и мотивирующим
            - Конкретным и информативным
            - Дружелюбным и welcoming
            - Профессиональным
            - Не менее 300 слов

            Используй эмодзи для выделения ключевых моментов.
            """

            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.7
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"❌ Error generating advanced description: {e}")
            return self._generate_fallback_description(club_data)

    def _generate_fallback_names(self, club_data: Dict[str, Any]) -> List[str]:
        """Резервные названия"""
        base_names = []
        idea = club_data.get('main_idea', '')
        category = club_data.get('category', '')

        for i in range(1, self.max_name_suggestions + 1):
            base_names.extend([
                f'{category.title()} {idea.title()} Club',
                f'{idea.title()} Community',
                f'{category.title()} Friends',
                f'{idea.title()} Hub',
                f'{category.title()} Center',
                f'{idea.title()} Association',
                f'{category.title()} Network',
                f'{idea.title()} Society'
            ])

        return list(set(base_names))[:self.max_name_suggestions]

    def _generate_fallback_description(self, club_data: Dict[str, Any]) -> str:
        """Резервное описание"""
        name = club_data.get('name', 'Наш клуб')
        idea = club_data.get('main_idea', 'интересы участников')
        category = club_data.get('category', 'различные активности')

        return f"""
        🎉 Добро пожаловать в {name}!

        Мы - сообщество единомышленников, объединенных общей страстью к {idea}. Наш клуб создает пространство для {
            category
        } и развития новых идей.

        🤝 Для кого этот клуб:
        - Люди, увлеченные {idea}
        - Желающие найти единомышленников
        - Стремящиеся к личностному росту
        - Готовые делиться знаниями и опытом

        📅 Что мы делаем:
        • Регулярные встречи и мероприятия
        • Обмен опытом и знаниями
        • Совместные проекты
        • Поддержка и вдохновение

        🚀 Присоединяйтесь к нам и станьте частью удивительного сообщества!
        """

    def _update_session(self, user_id: int, session: Dict[str, Any]):
        """Обновляем сессию в кэше"""
        cache_key = f"club_creation_session_{user_id}"
        cache.set(cache_key, session, 3600)  # 1 час


# Глобальный экземпляр агента
club_creation_agent = None


def get_club_creation_agent():
    """Получаем экземпляр агента по созданию клубов"""
    global club_creation_agent
    if club_creation_agent is None:
        club_creation_agent = ClubCreationAgent()
    return club_creation_agent