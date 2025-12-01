#!/usr/bin/env python3
"""
🤖 Conversational AI Agent for UnitySphere
Улучшенный AI агент с естественным общением и широким контекстом
"""

import json
import re
import random
from typing import Dict, List, Any, Optional
from datetime import datetime
import os

class ConversationalAIConsultant:
    """
    🤖 Conversational AI консультант с естественным общением
    """

    def __init__(self):
        self.conversation_state = "greeting"
        self.collected_data = {}
        self.conversation_history = []
        self.user_preferences = {}

        # Более естественные ответы
        self.greeting_variations = [
            "Привет! 😊 Я помогу создать твой фан-клуб. О чем мечтаешь?",
            "Здравствуй! 🚀 Давай создадим крутой клуб вместе!",
            "Приветствую! 🎯 Есть идея для нового клуба?",
            "Hey! 💫 Хочешь создать сообщество по своим интересам?"
        ]

        self.club_type_variations = [
            "Круто! 🎯 О чем будет твой клуб? Вот что популярно:",
            "Отлично! 🚀 Выбери направление:",
            "Прикольно! 🎨 Какое направление тебе ближе?",
            "Здорово! 💡 Что за клуб ты хочешь создать?"
        ]

    def get_natural_greeting(self):
        """Получить естественное приветствие"""
        return random.choice(self.greeting_variations)

    def get_natural_club_type_prompt(self):
        """Получить естественный запрос типа клуба"""
        return random.choice(self.club_type_variations)

    def detect_intent(self, message: str) -> str:
        """
        🧠 Распознавание намерений в сообщении с глубоким пониманием контекста
        """
        message_lower = message.lower().strip()

        # Команды (высокий приоритет)
        commands = {
            'help': ['помощь', 'help', 'справка', 'инструкция', 'что умеешь'],
            'reset': ['сброс', 'reset', 'начать сначала', 'заново', 'обновить'],
            'goodbye': ['пока', 'goodbye', 'прощай', 'хватит', 'стоп', 'закончить'],
            'find_clubs': ['найти', 'поиск', 'поищи', 'показать', 'есть ли', 'какие есть']
        }

        # Проверяем команды
        for cmd, keywords in commands.items():
            if any(keyword in message_lower for keyword in keywords):
                return cmd

        # Приветствия
        if any(greeting in message_lower for greeting in ['привет', 'здравствуй', 'hello', 'hi', 'hey', 'добрый день', 'доброе утро', 'добрый вечер']):
            return 'greeting'

        # Анализ намерения создать клуб с глубоким пониманием
        club_creation_patterns = [
            # Прямые формулировки
            ['создать', 'сделать', 'завести', 'открыть', 'запустить'],
            # Потребности
            ['хочу', 'нужен', 'надо', 'желаю', 'мечтаю', 'хочется'],
            # Общие слова
            ['клуб', 'сообщество', 'группа', 'фан-клуб', 'fan club', 'объединение', 'ассоциация']
        ]

        # Проверяем комбинацию паттернов для более точного распознавания
        has_creation_word = any(word in message_lower for word in club_creation_patterns[0])
        has_need_word = any(word in message_lower for word in club_creation_patterns[1])
        has_club_word = any(word in message_lower for word in club_creation_patterns[2])

        # Комбинированная проверка
        if (has_creation_word or has_need_word) and has_club_word:
            return 'create_club'

        # Проверяем интересы и хобби
        if any(interest in message_lower for interest in ['играю', 'занимаюсь', 'увлекаюсь', 'люблю', 'обожаю', 'фанат']):
            return 'create_club'

        # Проверяем вопросы
        if message_lower.endswith('?') or any(q in message_lower for q in ['как', 'что', 'где', 'когда', 'почему', 'зачем', 'сколько']):
            return 'question'

        # Проверяем упоминание конкретных интересов
        interests_keywords = [
            'игра', 'игры', 'game', 'gaming', 'программирование', 'код', 'coding', 'фото', 'фотография',
            'музыка', 'пение', 'guitar', 'рисование', 'art', 'кулинария', 'готовк', 'спорт', 'фитнес',
            'книги', 'чтение', 'travel', 'путешествия', 'кино', 'фильмы', 'шахмат', 'chess'
        ]

        if any(interest in message_lower for interest in interests_keywords):
            return 'create_club'

        return 'general'

    def get_club_suggestions(self) -> List[str]:
        """Получить предложения по типам клубов"""
        return [
            "🎮 Игровой клуб",
            "📸 Фото и видео",
            "🎵 Музыка и творчество",
            "📚 Книжный клуб",
            "🍳 Кулинарный клуб",
            "🏃 Спортивная команда",
            "🎨 Арт-студия",
            "💻 IT и технологии",
            "🎬 Кино-клуб",
            "🌍 Туризм и путешествия"
        ]

    def process_message(self, message: str, session_id: str = "default", history: List[Dict] = None) -> Dict[str, Any]:
        """
        🤖 Обработка сообщения пользователя
        """
        try:
            # Сохраняем историю
            if history:
                self.conversation_history = history[-10:]  # Ограничиваем историю

            # Определяем намерение
            intent = self.detect_intent(message)

            # Логируем для анализа
            print(f"📨 Session {session_id}: Intent = {intent}, Message = '{message[:50]}...'")

            # Обрабатываем в зависимости от состояния и намерения
            if intent == 'create_club':
                return self._handle_create_club(message, session_id)
            elif intent == 'greeting':
                return self._handle_greeting(message, session_id)
            elif intent == 'help':
                return self._handle_help(message, session_id)
            elif intent == 'reset':
                return self._handle_reset(message, session_id)
            elif intent == 'goodbye':
                return self._handle_goodbye(message, session_id)
            elif intent == 'find_clubs':
                return self._handle_find_clubs(message, session_id)
            elif intent == 'question':
                return self._handle_question(message, session_id)
            else:
                return self._handle_general(message, session_id)

        except Exception as e:
            print(f"❌ Error processing message: {e}")
            return self._get_error_response(str(e))

    def _handle_greeting(self, message: str, session_id: str) -> Dict[str, Any]:
        """Обработка приветствия"""
        response = self.get_natural_greeting()

        return {
            "success": True,
            "response": response,
            "state": "greeting",
            "quick_replies": [
                "🎮 Создать игровой клуб",
                "📸 Фото-клуб",
                "🎵 Музыкальный клуб",
                "❓ Как это работает?"
            ],
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }

    def _handle_create_club(self, message: str, session_id: str) -> Dict[str, Any]:
        """Обработка создания клуба"""
        # Определяем тип клуба из сообщения
        club_type = self._extract_club_type(message)

        if club_type:
            self.conversation_state = "club_name"
            self.collected_data['club_type'] = club_type

            response = f"Отлично! 🎯 {club_type} - это круто!\n\nКак назовем твой клуб? Придумай цепляющее имя!"
            return {
                "success": True,
                "response": response,
                "state": "club_name",
                "quick_replies": [
                    "Крутые {club_type}",
                    "Лучшие {club_type}",
                    "Наш {club_type}",
                    "Придумать самому"
                ],
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
        else:
            self.conversation_state = "club_type"
            response = self.get_natural_club_type_prompt()
            suggestions = self.get_club_suggestions()

            return {
                "success": True,
                "response": response,
                "state": "club_type",
                "quick_replies": suggestions,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }

    def _handle_club_name(self, message: str, session_id: str) -> Dict[str, Any]:
        """Обработка названия клуба"""
        club_name = message.strip()
        self.collected_data['club_name'] = club_name

        response = f"🔥 Отличное имя - '{club_name}'!\n\nТеперь расскажи, чем будет заниматься твой клуб? Что интересного будет происходить?"

        self.conversation_state = "club_description"
        return {
            "success": True,
            "response": response,
            "state": "club_description",
            "quick_replies": [
                "Встречи и мероприятия",
                "Обучение и развитие",
                "Соревнования и турниры",
                "Просто общение"
            ],
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }

    def _handle_club_description(self, message: str, session_id: str) -> Dict[str, Any]:
        """Обработка описания клуба"""
        description = message.strip()
        self.collected_data['description'] = description

        response = f"Понял! 📝 Твой клуб '{self.collected_data.get('club_name', '')}' будет заниматься:\n\n{description}\n\nТеперь дай знать, как с тобой связаться? Email, телефон или соцсети?"

        self.conversation_state = "club_contacts"
        return {
            "success": True,
            "response": response,
            "state": "club_contacts",
            "quick_replies": [
                "Оставить email",
                "Указать телефон",
                "Ссылку на соцсети",
                "Всё вместе"
            ],
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }

    def _handle_club_contacts(self, message: str, session_id: str) -> Dict[str, Any]:
        """Обработка контактов"""
        contacts = message.strip()
        self.collected_data['contacts'] = contacts

        club_name = self.collected_data.get('club_name', '')
        club_type = self.collected_data.get('club_type', '')
        description = self.collected_data.get('description', '')

        response = f"🎉 Отлично! Вот что у нас получилось:\n\n" \
                  f"**{club_name}**\n" \
                  f"Тип: {club_type}\n" \
                  f"Описание: {description}\n" \
                  f"Контакты: {contacts}\n\n" \
                  f"Готов создать этот крутой клуб? 💫"

        self.conversation_state = "confirmation"
        return {
            "success": True,
            "response": response,
            "state": "confirmation",
            "quick_replies": [
                "✅ Создать клуб!",
                "✏️ Внести изменения",
                "❌ Отменить",
                "🔄 Начать сначала"
            ],
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }

    def _handle_confirmation(self, message: str, session_id: str) -> Dict[str, Any]:
        """Обработка подтверждения"""
        message_lower = message.lower().strip()

        if any(word in message_lower for word in ['создать', 'да', 'готов', 'ок']):
            # Здесь можно добавить логику сохранения клуба в базу данных
            club_name = self.collected_data.get('club_name', '')
            response = f"🚀 Ура! Твой клуб '{club_name}' успешно создан!\n\n" \
                      f"🎉 Поздравляю с новым начинанием! Теперь у тебя есть классное сообщество.\n\n" \
                      f"💡 Совет: Не забудь пригласить друзей и начать первые мероприятия!\n\n" \
                      f"Хочешь создать еще один клуб или чем-то еще помочь?"

            self._reset_conversation()
            return {
                "success": True,
                "response": response,
                "state": "completed",
                "quick_replies": [
                    "🎮 Создать еще клуб",
                    "🔍 Найти другие клубы",
                    "❓ Задать вопрос",
                    "👋 Пока"
                ],
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
        else:
            response = "Понял! 🤔 Что хочешь изменить?"
            self.conversation_state = "modification"
            return {
                "success": True,
                "response": response,
                "state": "modification",
                "quick_replies": [
                    "Изменить название",
                    "Изменить описание",
                    "Изменить контакты",
                    "Начать сначала"
                ],
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }

    def _handle_help(self, message: str, session_id: str) -> Dict[str, Any]:
        """Обработка справки"""
        response = "🆘 Вот что я умею:\n\n" \
                  "• 🎮 **Создать клуб** - Помогу создать любой фан-клуб\n" \
                  "• 🔍 **Найти клубы** - Покажу существующие сообщества\n" \
                  "• ❓ **Задать вопрос** - Отвечу на любые вопросы\n" \
                  "• 🔄 **Сброс** - Начать сначала\n" \
                  "• 👋 **Пока** - Завершить диалог\n\n" \
                  "💡 Просто скажи, что хочешь, и я помогу!"

        return {
            "success": True,
            "response": response,
            "state": "help",
            "quick_replies": [
                "🎮 Создать клуб",
                "🔍 Найти клубы",
                "❓ Задать вопрос",
                "👋 Пока"
            ],
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }

    def _handle_reset(self, message: str, session_id: str) -> Dict[str, Any]:
        """Обработка сброса"""
        self._reset_conversation()
        response = "🔄 Отлично! Начинаем с чистого листа!\n\nЧем займемся? 😉"

        return {
            "success": True,
            "response": response,
            "state": "greeting",
            "quick_replies": [
                "🎮 Создать крутой клуб",
                "🔍 Посмотреть существующие",
                "❓ Интересуюсь возможностями",
                "💬 Просто поболтать"
            ],
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }

    def _handle_goodbye(self, message: str, session_id: str) -> Dict[str, Any]:
        """Обработка прощания"""
        response = "👋 Был рад помочь!\n\nЕсли захочется создать еще один крутой клуб или что-то еще - заходи!\n\nУдачи во всех начинаниях! ✨"

        return {
            "success": True,
            "response": response,
            "state": "goodbye",
            "action": "close_chat",
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }

    def _handle_find_clubs(self, message: str, session_id: str) -> Dict[str, Any]:
        """Обработка поиска клубов"""
        response = "🔍 Ищу интересные клубы...\n\n" \
                  "🎮 **Игровой клуб 'Pixel Masters'** - Для ценителей игр\n" \
                  "📸 **Фото-студия 'Golden Lens'** - Любителям фотографии\n" \
                  "🎵 **Музыкальная гостиная 'Sound Waves'** - Для меломанов\n" \
                  "📚 **Книжный клуб 'Page Turners'** - Обсудим литературу\n" \
                  "🍳 **Кулинарный уголок 'Tasty Moments'** - Готовим вместе\n\n" \
                  "💡 Хочешь подробнее о каком-то из них?"

        return {
            "success": True,
            "response": response,
            "state": "showing_clubs",
            "quick_replies": [
                "🎮 Расскажи про игровые",
                "📸 Про фото-клубы",
                "🎵 Про музыку",
                "📚 Про книги"
            ],
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }

    def _handle_question(self, message: str, session_id: str) -> Dict[str, Any]:
        """Обработка вопроса"""
        # Можно интегрировать с OpenAI для умных ответов
        response = "🤔 Интересный вопрос!\n\n" \
                  "Я могу помочь с:\n" \
                  "• 🎮 Созданием фан-клубов\n" \
                  "• 🔍 Поиском существующих сообществ\n" \
                  "• 💡 Советами по развитию клубов\n" \
                  "• ❓ Ответами на вопросы о платформе\n\n" \
                  "Что конкретно тебя интересует?"

        return {
            "success": True,
            "response": response,
            "state": "answering_question",
            "quick_replies": [
                "Как создать клуб?",
                "Что такое фан-клуб?",
                "Сколько это стоит?",
                "💡 Другой вопрос"
            ],
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }

    def _handle_general(self, message: str, session_id: str) -> Dict[str, Any]:
        """Обработка общего сообщения"""
        response = "😊 Понял тебя!\n\n" \
                  "Чем займемся?\n" \
                  "• 🎮 Создадим крутой клуб?\n" \
                  "• 🔍 Посмотрим существующие сообщества?\n" \
                  "• 💬 Просто поговорим?\n\n" \
                  "Выбирай, что интересно! ✨"

        return {
            "success": True,
            "response": response,
            "state": "general",
            "quick_replies": [
                "🎮 Создать клуб",
                "🔍 Посмотреть клубы",
                "❓ Задать вопрос",
                "💬 Поговорить"
            ],
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }

    def _extract_club_type(self, message: str) -> Optional[str]:
        """Извлечь тип клуба из сообщения с глубоким пониманием контекста"""
        message_lower = message.lower()

        # Расширенные паттерны для распознавания типов клубов
        club_patterns = {
            # Игровые и развлекательные
            'шахматы': ['шахмат', 'шахматн', 'chess', 'chess club', 'шахматный'],
            'игры': ['игра', 'игр', 'game', 'gaming', 'gamer', 'видеоигр', 'киберспорт',
                     'computer games', 'video games', 'play', 'играть', 'гейминг'],
            'настолки': ['настолк', 'настольн', 'board game', 'настольные игры', 'tabletop',
                         'ролевк', 'ролевые', 'D&D', 'днд', 'дндшник'],

            # Технологии и IT
            'программирование': ['программ', 'код', 'coding', 'it', 'tech', 'разработка',
                               'development', 'developer', 'программист', 'software', 'computer'],
            'робототехника': ['робот', 'робототехник', 'robot', 'robotics', 'мехатроник'],
            'кибербезопасность': ['кибер', 'кибербезопасн', 'cyber', 'security', 'hacking', 'hack'],

            # Творчество и искусство
            'фотография': ['фото', 'camera', 'съемка', 'photography', 'фотограф', 'фотосъемк'],
            'рисование': ['рисова', 'art', 'рисован', 'drawing', 'painting', 'живопись', 'карандаш'],
            'дизайн': ['дизайн', 'design', 'graphic', 'графика', 'веб-дизайн', 'web design'],
            'музыка': ['музыка', 'пение', 'guitar', 'instrument', 'музыкант', 'band', 'группа',
                      'compose', 'composition', 'композиция'],
            'танцы': ['танц', 'dance', 'танцевальн', 'балет', 'хореография', 'choreography'],
            'театр': ['театр', 'актер', 'acting', 'актерск', 'драма', 'драматический'],

            # Спорт и здоровье
            'спорт': ['спорт', 'фитнес', 'gym', 'тренировк', 'sport', 'physical', 'активн'],
            'фитнес': ['фитнес', 'gym', 'тренажер', 'workout', 'exercise', 'упражнения'],
            'йога': ['йога', 'yoga', 'медитация', 'meditation', 'расслабление'],
            'бег': ['бег', 'jogging', 'running', 'marathon', 'полумарафон'],
            'борьба': ['борьба', 'wrestling', 'борцов', 'дзюдо', ' judo', 'каратэ', 'karate'],

            # Образование и наука
            'книги': ['книга', 'reading', 'чтение', 'literature', 'literary', 'литература'],
            'языки': ['язык', 'language', 'english', 'немецкий', 'французский', 'китайский',
                     'language learning', 'изучение языков'],
            'наука': ['наука', 'science', 'ученый', 'research', 'исследование', 'эксперимент'],
            'математика': ['математик', 'math', 'алгебра', 'геометрия', 'тригонометрия'],

            # Кулинария и еда
            'кулинария': ['кулинар', 'еда', 'готов', 'cook', 'culinary', 'рецепт', 'рецепты',
                         'cooking', 'рецепт', 'блюдо'],
            'выпечка': ['выпечк', 'baking', 'cake', 'торт', 'хлеб', 'confectionery'],
            'вегетарианство': ['вегетариан', 'vegan', 'растительная', 'plant-based', 'здоровое питание'],

            # Путешествия и туризм
            'путешествия': ['путешеств', 'travel', 'туризм', 'tourism', 'trip', 'поездка',
                           'expedition', 'экспедиция', 'туры'],
            'пешеходные прогулки': ['пешеходн', 'поход', 'hiking', 'trekking', 'mountain', 'горы'],

            # Социальные и волонтерские
            'волонтерство': ['волонтер', 'благотворительность', 'charity', 'help', 'помощь',
                            'social work', 'социальная деятельность'],
            'экология': ['эколог', 'environment', 'green', 'зеленый', 'природа', 'nature',
                        'sustainability', 'устойчивость'],

            # Бизнес и предпринимательство
            'бизнес': ['бизнес', 'business', 'предприниматель', 'entrepreneur', 'стартап',
                      'startup', 'коммерция'],
            'инвестиции': ['инвестиции', 'investments', 'финансы', 'finance', 'money', 'деньги'],

            # Автомобильные
            'автомобили': ['автомобиль', 'car', 'машина', 'auto', 'авто', 'мотоцикл', 'motorcycle']
        }

        # Поиск по паттернам
        for club_type, patterns in club_patterns.items():
            if any(pattern in message_lower for pattern in patterns):
                return club_type.capitalize()

        # Анализ интересов и увлечений
        interest_patterns = {
            'шахматы': ['играю в шахматы', 'обожаю шахматы', 'fan of chess', 'love chess'],
            'игры': ['играю в игры', 'геймер', 'gamer', 'игрок'],
            'программирование': ['программирую', 'пишу код', 'code', 'develop'],
            'фотография': ['фоткаю', 'снимаю', 'photograph', 'shoot'],
            'музыка': ['играю на', 'пою', 'музыкант', 'musician'],
            'спорт': ['занимаюсь спортом', 'тренируюсь', 'workout', 'train'],
            'чтение': ['читаю книги', 'книжный червь', 'bookworm', 'читаю']
        }

        for club_type, patterns in interest_patterns.items():
            if any(pattern in message_lower for pattern in patterns):
                return club_type.capitalize()

        # Если не распознали, возвращаем None
        return None

    def _reset_conversation(self):
        """Сбросить состояние разговора"""
        self.conversation_state = "greeting"
        self.collected_data = {}
        self.conversation_history = []

    def _get_error_response(self, error_msg: str) -> Dict[str, Any]:
        """Получить ответ при ошибке"""
        return {
            "success": False,
            "response": "😔 Ой, что-то пошло не так...\n\n" \
                      "Попробуй, пожалуйста, еще раз или скажи 'помощь' если нужна помощь! 🤗",
            "state": "error",
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }


def process_conversational_message(message: str, session_id: str = "default", history: List[Dict] = None) -> Dict[str, Any]:
    """
    🚀 Функция для обработки сообщений (интерфейс для сервера)
    """
    agent = ConversationalAIConsultant()
    return agent.process_message(message, session_id, history)


if __name__ == "__main__":
    # Тестирование
    agent = ConversationalAIConsultant()

    print("🧪 Тестируем Conversational AI агента...")
    print("=" * 50)

    test_messages = [
        "Привет!",
        "Хочу создать шахматный клуб",
        "Клуб программирования",
        "Tech Masters",
        "Мы будем изучать Python и создавать проекты",
        "dev@example.com, +7 707 123-45-67",
        "Создать клуб!"
    ]

    session_id = "test_session"
    for i, msg in enumerate(test_messages):
        print(f"\n📝 Сообщение {i+1}: {msg}")
        result = agent.process_message(msg, session_id)
        print(f"💬 AI: {result['response']}")
        print(f"📍 Состояние: {result['state']}")
        if result.get('quick_replies'):
            print(f"ButtonTitles: {', '.join(result['quick_replies'])}")
        print("-" * 30)