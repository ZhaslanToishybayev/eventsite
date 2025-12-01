"""
🤖 Интерактивный AI Консультант - Задает вопросы пользователю для создания клуба
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Добавляем путь к Django проекту
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from actionable_ai_consultant import ActionableAIConsultant
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session

User = get_user_model()

class InteractiveAIConsultant:
    def __init__(self):
        self.ai = ActionableAIConsultant()

    def get_creation_state(self, session_key):
        """Получаем состояние создания клуба из сессии"""
        if not session_key:
            print(f"DEBUG: get_creation_state - no session_key provided")
            return {}

        try:
            session = Session.objects.get(session_key=session_key)
            state = session.get_decoded().get('club_creation_state', {})
            print(f"DEBUG: get_creation_state - session_key={session_key}, state={state}")
            return state
        except Session.DoesNotExist:
            print(f"DEBUG: get_creation_state - session not found for key={session_key}")
            return {}

    def set_creation_state(self, session_key, state):
        """Сохраняем состояние создания клуба в сессию"""
        if not session_key:
            return

        try:
            # Используем Django session framework правильно
            from django.contrib.sessions.models import Session
            from django.contrib.sessions.serializers import JSONSerializer

            session = Session.objects.get(session_key=session_key)
            session_data = session.get_decoded()
            session_data['club_creation_state'] = state

            # Используем Django сериализатор для правильного формата
            serializer = JSONSerializer()
            session.session_data = serializer.dumps(session_data)
            session.save()
            print(f"DEBUG: set_creation_state - saved state for session {session_key}: {state}")
        except Session.DoesNotExist:
            print(f"DEBUG: set_creation_state - session not found for key {session_key}, cannot save state")
            pass  # Сессия может быть создана позже

    def process_user_message(self, message, user_email=None, session_key=None):
        """Обработка сообщения пользователя с интерактивным созданием клуба"""
        message_lower = message.lower().strip()

        # Получаем состояние из сессии
        creation_state = self.get_creation_state(session_key)
        current_step = creation_state.get('step')
        club_data = creation_state.get('data', {})

        print(f"DEBUG: session_key={session_key}, creation_state={creation_state}, current_step={current_step}")

        # Проверяем, находится ли пользователь в процессе создания клуба
        if current_step:
            response = self.handle_club_creation_step(message, user_email, creation_state, session_key)
            return response

        # Проверяем запрос на создание клуба
        if any(keyword in message_lower for keyword in ['создать клуб', 'создать фан-клуб', 'хочу создать', 'сделать клуб', 'создание клуба']):
            return self.start_club_creation(session_key)

        # Проверяем другие команды
        if any(keyword in message_lower for keyword in ['клуб', 'фан-клуб']):
            return self.ai.process_user_message(message, user_email)

        # Для остальных сообщений используем обычного AI
        return self.ai.process_user_message(message, user_email)

    def start_club_creation(self, session_key):
        """Начинаем процесс создания клуба - задаем первый вопрос"""
        self.set_creation_state(session_key, {
            'step': 'name',
            'data': {}
        })

        return """🎯 [INTERACTIVE MODE] Отлично! Давай создадим твой фан-клуб! Я задам тебе несколько вопросов:

**📝 Вопрос 1:** Как будет называться твой клуб?

Напиши название, например: "Шахматная Академия", "Клуб любителей книг" и т.д."""

    def handle_club_creation_step(self, message, user_email, creation_state, session_key):
        """Обрабатываем шаг создания俱乐部"""
        current_step = creation_state.get('step')
        club_data = creation_state.get('data', {})

        # Сохраняем ответ пользователя
        if current_step == 'name':
            club_data['name'] = message.strip()
            creation_state['data'] = club_data
            creation_state['step'] = 'description'
            self.set_creation_state(session_key, creation_state)
            return """✅ Отличное название!

**📝 Вопрос 2:** Опиши свой клуб (минимум 100 символов). Расскажи:
- Чем будет заниматься клуб
- Для кого он предназначен
- Какие мероприятия будет проводить

Например: "Это место где любители шахмат могут развивать мастерство, участвовать в турнирах и общаться с единомышленниками"."""

        elif current_step == 'description':
            description = message.strip()
            if len(description) < 100:
                return """⚠️ Описание слишком короткое. Нужно минимум 100 символов.

Пожалуйста, подробнее расскажи о своем клубе."""

            club_data['description'] = description
            creation_state['data'] = club_data
            creation_state['step'] = 'category'
            self.set_creation_state(session_key, creation_state)
            return """📝 Отлично!

**📝 Вопрос 3:** К какой категории относится твой клуб?
Выбери из:
- Спорт
- Музыка
- Искусство
- Игры
- Книги
- Фильмы
- Технологии
- Образование
- Другое

Напиши одну из категорий."""

        elif current_step == 'category':
            club_data['category'] = message.strip()
            creation_state['data'] = club_data
            creation_state['step'] = 'city'
            self.set_creation_state(session_key, creation_state)
            return """✅ Хорошо!

**📝 Вопрос 4:** В каком городе будет located твой клуб?

Например: Алматы, Астана, Шымкент и т.д."""

        elif current_step == 'city':
            club_data['city'] = message.strip()
            creation_state['data'] = club_data
            creation_state['step'] = 'email'
            self.set_creation_state(session_key, creation_state)
            return """📝 Отлично!

**📝 Вопрос 5:** Какой email для связи с клубом?

Например: club@gmail.com, myclub@mail.ru и т.д."""

        elif current_step == 'email':
            email = message.strip()
            if '@' not in email:
                return """⚠️ Некорректный email. Пожалуйста, введи правильный email адрес.

Например: club@gmail.com"""

            club_data['email'] = email
            creation_state['data'] = club_data
            creation_state['step'] = 'phone'
            self.set_creation_state(session_key, creation_state)
            return """✅ Email принят!

**📝 Вопрос 6:** Телефон для связи (необязательно)
Если не хочешь указывать, напиши "нет"

Например: +7 (701) 123-45-67"""

        elif current_step == 'phone':
            phone = message.strip()
            if phone.lower() != 'нет':
                club_data['phone'] = phone
            else:
                club_data['phone'] = '+77010000001'  # Телефон по умолчанию

            creation_state['data'] = club_data
            creation_state['step'] = 'address'
            self.set_creation_state(session_key, creation_state)
            return """📝 Принято!

**📝 Вопрос 7:** Адрес встреч клуба (необязательно)
Если не знаешь, напиши "нет"

Например: "Алматы, проспект Абая 89" или "Кафе в центре города"."""

        elif current_step == 'address':
            address = message.strip()
            if address.lower() != 'нет':
                club_data['address'] = address
            else:
                club_data['address'] = 'Алматы, центр города'  # Адрес по умолчанию

            creation_state['data'] = club_data
            # Завершаем сбор данных и создаем клуб
            result = self.create_club(club_data, user_email)
            # Очищаем состояние после успешного создания
            if result and 'success' in result and result['success']:
                self.set_creation_state(session_key, {})
            return result

    def create_club(self, club_data, user_email):
        """Создаем клуб в базе данных"""
        try:
            # Добавляем данные по умолчанию
            full_club_data = {
                'name': club_data.get('name'),
                'description': club_data.get('description'),
                'category': club_data.get('category'),
                'city': club_data.get('city'),
                'email': club_data.get('email'),
                'phone': club_data.get('phone', '+77010000001'),
                'address': club_data.get('address', 'Алматы, центр города'),
                'activities': club_data.get('activities', 'Регулярные встречи и мероприятия'),
                'target_audience': club_data.get('target_audience', 'Все желающие'),
                'skills_developed': club_data.get('skills_developed', 'Развитие навыков'),
                'tags': club_data.get('tags', 'клуб, сообщество')
            }

            # Создаем клуб
            result = self.ai.create_club_in_database(full_club_data, user_email)

            # Очищаем состояние
            self.creation_state = {}

            if result['success']:
                return f"""🎉 ПОЗДРАВЛЯЮ! Твой клуб успешно создан!

**📋 Информация о клубе:**
• Название: {result['name']}
• ID клуба: {result['club_id']}
• Город: {result['city']}
• Email: {result['email']}

**🔧 Что дальше:**
1. **Зайди в админку**: Перейди в личный кабинет и найди свой клуб
2. **Добавь фото**: Загрузи логотип и фотографии клуба
3. **Создай первое мероприятие**: Организуй знакомство участников
4. **Расскажи друзьям**: Пригласи первых участников

**📱 Твой клуб теперь на fan-club.kz!**
Ссылка: https://fan-club.kz/clubs/{result['club_id']}

Хочешь, помогу с первым мероприятием или продвижением клуба? 😊"""
            else:
                return f"""❌ Ошибка при создании клуба: {result['error']}

Пожалуйста, попробуй еще раз или свяжись с администратором."""

        except Exception as e:
            self.creation_state = {}  # Очищаем состояние при ошибке
            return f"""❌ Произошла ошибка: {str(e)}

Пожалуйста, попробуй начать процесс создания клуба заново."""

    def get_club_creation_template(self):
        """Возвращаем стандартную форму (если нужно)"""
        return self.ai.get_club_creation_template()