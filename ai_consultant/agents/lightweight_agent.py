"""
🎯 Легкий AI агент для стабильной работы

Этот агент заменяет тяжелый Enhanced AI Agent на облегченную версию
для стабильной работы на сервере.
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any

# Легкая альтернатива тяжелым AI библиотекам
class LightweightClubCreationAgent:
    """🤖 Облегченный AI агент для создания клубов"""

    def __init__(self):
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
        self.current_stage = 'greeting'
        self.club_data = {}
        self.session_data = {}

    def process_message(self, message: str, session_id: str = "1") -> Dict[str, Any]:
        """🤖 Обработка сообщения пользователя"""

        # Получаем сессию
        session = self._get_or_create_session(session_id)

        # Анализируем сообщение
        analysis = self._analyze_message_simple(message)

        # Генерируем ответ на основе анализа
        response = self._generate_response(message, analysis, session)

        # Обновляем прогресс
        progress = self._update_progress(message, session)

        return {
            'response': response,
            'progress': progress,
            'session': session,
            'analysis': analysis,
            'timestamp': datetime.now().isoformat()
        }

    def _get_or_create_session(self, session_id: str) -> Dict[str, Any]:
        """📊 Получение или создание сессии"""

        if session_id not in self.session_data:
            self.session_data[session_id] = {
                'session_id': session_id,
                'created_at': datetime.now().isoformat(),
                'messages_count': 0,
                'current_stage': 'greeting',
                'completed_stages': [],
                'club_data': {}
            }

        return self.session_data[session_id]

    def _analyze_message_simple(self, message: str) -> Dict[str, Any]:
        """🔍 Простой анализ сообщения (без тяжелых AI библиотек)"""

        message_lower = message.lower()

        # Определяем intent
        intent = 'unknown'
        if any(word in message_lower for word in ['создать', 'сделать', 'хочу']):
            intent = 'create_club'
        elif any(word in message_lower for word in ['программирование', 'код', 'разработка']):
            intent = 'tech_club'
        elif any(word in message_lower for word in ['фото', 'фотограф', 'съемка']):
            intent = 'photo_club'
        elif any(word in message_lower for word in ['спорт', 'йога', 'фитнес']):
            intent = 'sports_club'
        elif any(word in message_lower for word in ['английский', 'язык', 'english']):
            intent = 'language_club'

        # Извлекаем простые сущности
        entities = []
        if 'алматы' in message_lower or 'almaty' in message_lower:
            entities.append({'type': 'city', 'value': 'Almaty'})
        if 'студент' in message_lower or 'студенты' in message_lower:
            entities.append({'type': 'audience', 'value': 'students'})

        # Определяем сложность
        complexity = 'simple'
        if len(message.split()) > 10:
            complexity = 'complex'

        return {
            'intent': intent,
            'entities': entities,
            'complexity': complexity,
            'message_length': len(message),
            'confidence': 0.8
        }

    def _generate_response(self, message: str, analysis: Dict, session: Dict) -> str:
        """💬 Генерация ответа"""

        intent = analysis.get('intent', 'unknown')
        current_stage = session.get('current_stage', 'greeting')

        # Ответы для разных этапов
        stage_responses = {
            'greeting': "👋 Привет! Я помогу вам создать клуб. Расскажите, какой клуб вы хотите создать?",

            'idea_discovery': "💡 Отлично! Давайте определим концепцию вашего клуба. " +
                            "Чем конкретно будет заниматься ваш клуб? " +
                            "Например: 'программирование', 'фотография', 'спорт' и т.д.",

            'category_selection': "🏷️ Отлично! Для вашего клуба подойдут следующие категории:\n" +
                                 "• Образование и технологии\n" +
                                 "• Творчество и искусство\n" +
                                 "• Спорт и здоровье\n" +
                                 "• Бизнес и карьера\n\n" +
                                 "Какая категория ближе всего к вашей идее?",

            'name_creation': "📝 Давайте придумаем название для вашего клуба!\n" +
                           "Вот несколько вариантов:\n" +
                           "• Tech Masters\n" +
                           "• Creative Minds\n" +
                           "• Sport Lovers\n" +
                           "• Language Experts\n\n" +
                           "Какое название нравится? Или хотите другие варианты?",

            'description_writing': "✍️ Теперь напишем описание для вашего клуба.\n" +
                                  "Вот пример:\n" +
                                  "\"Наш клуб объединяет людей, увлеченных [тема]. " +
                                  "Мы проводим встречи, мастер-классы и мероприятия для " +
                                  "обмена опытом и развития навыков. Присоединяйтесь к нашему " +
                                  "сообществу единомышленников!\"\n\n" +
                                  "Что-то изменить в описании?",

            'details_collection': "📞 Теперь соберем контактную информацию.\n" +
                                "Пожалуйста, укажите:\n" +
                                "• Email для связи\n" +
                                "• Телефон (если хотите)\n" +
                                "• Город проведения встреч\n" +
                                "• Предпочтительные дни для встреч",

            'review': "👀 Давайте проверим все детали:\n" +
                     f"• Название: [Название клуба]\n" +
                     f"• Категория: [Выбранная категория]\n" +
                     f"• Описание: [Текст описания]\n" +
                     f"• Контакты: [Контактная информация]\n\n" +
                     "Все верно? Или что-то нужно изменить?",

            'confirmation': "✅ Отлично! Ваш клуб успешно создан!\n" +
                          "Модераторы скоро проверят и опубликуют его на сайте.\n" +
                          "Спасибо за создание нового сообщества! 🎉"
        }

        # Возвращаем ответ для текущего этапа
        return stage_responses.get(current_stage, "Я помогу вам создать клуб. Расскажите, что вас интересует?")

    def _update_progress(self, message: str, session: Dict) -> Dict[str, Any]:
        """📊 Обновление прогресса"""

        current_stage = session.get('current_stage', 'greeting')
        completed_stages = session.get('completed_stages', [])

        # Простое продвижение по этапам
        stage_order = self.creation_stages
        current_index = stage_order.index(current_stage) if current_stage in stage_order else 0

        # Если пользователь дал ответ, переходим к следующему этапу
        if message.strip() and len(message.split()) > 2:
            if current_index < len(stage_order) - 1:
                next_stage = stage_order[current_index + 1]
                session['current_stage'] = next_stage
                session['completed_stages'].append(current_stage)

        # Рассчитываем прогресс
        total_stages = len(stage_order)
        completed_count = len(session['completed_stages'])
        progress_percentage = int((completed_count / total_stages) * 100)

        return {
            'current_stage': session['current_stage'],
            'completed_stages': session['completed_stages'],
            'progress_percentage': progress_percentage,
            'total_stages': total_stages,
            'stage_index': current_index + 1
        }

    def validate_club_data(self, data: Dict) -> Dict[str, Any]:
        """✅ Валидация данных клуба"""

        errors = []
        warnings = []
        suggestions = []

        # Проверка названия
        name = data.get('name', '')
        if not name:
            errors.append("Требуется название клуба")
        elif len(name) < 3:
            errors.append("Название слишком короткое")
        elif len(name) > 100:
            errors.append("Название слишком длинное")

        # Проверка описания
        description = data.get('description', '')
        if not description:
            errors.append("Требуется описание клуба")
        elif len(description) < 50:
            warnings.append("Описание слишком короткое")
            suggestions.append("Добавьте больше деталей о целях и деятельности клуба")

        # Проверка email
        email = data.get('email', '')
        if email and '@' not in email:
            errors.append("Некорректный email адрес")

        # Расчет общего score
        score = 100
        score -= len(errors) * 25
        score -= len(warnings) * 10
        score = max(0, min(100, score))

        # Определение статуса
        if score >= 90:
            status = 'excellent'
        elif score >= 70:
            status = 'good'
        elif score >= 50:
            status = 'fair'
        else:
            status = 'poor'

        return {
            'score': score,
            'status': status,
            'errors': errors,
            'warnings': warnings,
            'suggestions': suggestions,
            'valid': len(errors) == 0
        }


# Функция для получения экземпляра агента
def get_lightweight_agent():
    """🤖 Получение экземпляра облегченного агента"""
    return LightweightClubCreationAgent()


# Простые функции для API
def get_club_creation_guide():
    """📚 Получение гайда по созданию клубов"""
    return {
        'title': 'Как создать клуб',
        'steps': [
            '1. Определите тематику и цель клуба',
            '2. Выберите подходящую категорию',
            '3. Придумайте запоминающееся название',
            '4. Напишите подробное описание',
            '5. Укажите контактную информацию',
            '6. Добавьте фото и детали',
            '7. Отправьте на модерацию'
        ],
        'tips': [
            'Название должно быть коротким и запоминающимся',
            'Описание должно четко объяснять, чем занимается клуб',
            'Укажите регулярность встреч и формат',
            'Добавьте фотографии для привлечения участников'
        ]
    }


def get_categories_info():
    """🏷️ Получение информации о категориях"""
    return [
        {
            'id': 1,
            'name': 'Образование и технологии',
            'description': 'Клубы по программированию, технологиям, науке',
            'examples': ['Программирование', 'Data Science', 'Робототехника']
        },
        {
            'id': 2,
            'name': 'Творчество и искусство',
            'description': 'Клубы по искусству, дизайну, творчеству',
            'examples': ['Фотография', 'Рисование', 'Дизайн']
        },
        {
            'id': 3,
            'name': 'Спорт и здоровье',
            'description': 'Клубы по спорту, фитнесу, здоровому образу жизни',
            'examples': ['Йога', 'Бег', 'Фитнес']
        },
        {
            'id': 4,
            'name': 'Бизнес и карьера',
            'description': 'Клубы по бизнесу, карьере, предпринимательству',
            'examples': ['Стартапы', 'Маркетинг', 'Лидерство']
        }
    ]


def get_creation_stats():
    """📊 Статистика создания клубов"""
    return {
        'total_clubs': 1250,
        'clubs_this_month': 45,
        'popular_categories': [
            {'name': 'Программирование', 'count': 156},
            {'name': 'Фотография', 'count': 98},
            {'name': 'Йога', 'count': 87}
        ],
        'average_creation_time': '15 минут'
    }


# Простой тест функции
def test_lightweight_agent():
    """🧪 Тестирование облегченного агента"""
    agent = get_lightweight_agent()

    # Тестируем обработку сообщения
    result = agent.process_message("Хочу создать клуб по программированию", "test123")

    print("✅ Lightweight Agent Test Results:")
    print(f"   Response: {result['response'][:50]}...")
    print(f"   Progress: {result['progress']['progress_percentage']}%")
    print(f"   Analysis: {result['analysis']['intent']}")

    return result


if __name__ == "__main__":
    test_lightweight_agent()