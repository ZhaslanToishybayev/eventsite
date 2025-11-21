#!/usr/bin/env python3
"""
🤖 Интерактивный создатель клубов через ИИ консультанта
Позволяет пользователям создавать клубы через диалоговый интерфейс
"""

import json
import uuid
import re
import html
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.decorators.debug import sensitive_post_parameters
from clubs.models import Club, ClubCategory, City

# 🔐 ИМПОРТ МОДУЛЯ БЕЗОПАСНОСТИ
from ai_consultant.security import (
    SecurityValidator,
    sanitize_user_input,
    validate_user_message,
    log_security_event
)

# 🔧 ВРЕМЕННОЕ РЕШЕНИЕ: Используем прямые импорты моделей для персистентности
# TODO: Исправить импорты сервисов после рефакторинга
from ai_consultant.models import ConversationState, AISessionLog, ClubCreationRequest
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ObjectDoesNotExist
from typing import Dict, Any
import uuid
import logging

logger = logging.getLogger(__name__)

class AIClubCreator:
    def __init__(self):
        # Больше не нужно хранить состояние в памяти - используем базу данных
        pass

    def get_session_state(self, session_id, user=None, user_agent=None, ip_address=None):
        """Получить или создать состояние сессии из базы данных"""
        try:
            # Сначала ищем существующее состояние
            state = ConversationState.objects.get(session_id=session_id)

            # Проверяем не истекла ли сессия (24 часа по умолчанию)
            from django.utils import timezone
            from datetime import timedelta
            if timezone.now() > state.expires_at:
                logger.info(f"Session {session_id} expired, creating new one")
                state = self._create_new_state(session_id, user, user_agent, ip_address)

            return state

        except ConversationState.DoesNotExist:
            # Создаем новое состояние
            return self._create_new_state(session_id, user, user_agent, ip_address)

    def _update_session_state(self, session_id: str, stage: str = None,
                             data_updates: Dict[str, Any] = None, last_question: str = None):
        """
        Helper-метод для обновления состояния сессии
        Временно заменяет conversation_state_service.update_state
        """
        try:
            from django.db import transaction
            with transaction.atomic():
                state = ConversationState.objects.get(session_id=session_id)

                if stage is not None:
                    state.stage = stage

                if data_updates:
                    for key, value in data_updates.items():
                        current_data = state.data or {}
                        current_data[key] = value
                        state.data = current_data

                if last_question:
                    state.last_question = last_question

                # Автоматически обновляем прогресс на основе этапа
                stage_progress_map = {
                    'welcome': 0,
                    'name': 1,
                    'category': 2,
                    'description': 3,
                    'email': 4,
                    'phone': 5,
                    'confirm': 6,
                    'done': 100
                }
                state.progress = stage_progress_map.get(stage, 0)

                state.save()
                return state

        except Exception as e:
            logger.error(f"Failed to update session state: {e}")
            return None

    def _create_new_state(self, session_id, user=None, user_agent=None, ip_address=None):
        """Создать новое состояние对话"""
        from django.db import transaction
        from django.utils import timezone
        from datetime import timedelta

        with transaction.atomic():
            state = ConversationState.objects.create(
                session_id=session_id,
                stage='welcome',
                data={},
                progress=0,
                user=user,
                user_agent=user_agent,
                ip_address=ip_address,
                expires_at=timezone.now() + timedelta(hours=24)
            )

            # Логируем создание состояния
            log_security_event('conversation_state_created', {
                'session_id': session_id,
                'user_id': user.id if user else None,
                'ip_address': ip_address
            })

            return state

    def extract_email(self, text):
        """Извлечь email из текста"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        return match.group(0) if match else None

    def extract_phone(self, text):
        """Извлечь телефон из текста"""
        # Удаляем все нецифровые символы кроме +
        phone = re.sub(r'[^\d+]', '', text)
        # Ищем последовательность из 10-15 цифр (может включать +)
        phone_match = re.search(r'\+?\d{10,15}', phone)
        return phone_match.group(0) if phone_match else None

    def validate_email(self, email):
        """🔐 Расширенная проверка валидности email с защитой безопасности"""
        if not email:
            return False, "Email обязателен"

        # Используем улучшенную валидацию из модуля безопасности
        is_valid, error_msg = SecurityValidator.validate_email_advanced(email.strip())
        if not is_valid:
            log_security_event('email_validation_failed', {
                'email': email[:50] + '...' if len(email) > 50 else email,
                'error': error_msg
            })
        return is_valid, error_msg

    def validate_phone(self, phone):
        """🔐 Расширенная проверка валидности телефона с защитой безопасности"""
        if not phone:
            return False, "Телефон обязателен"

        # Используем улучшенную валидацию из модуля безопасности
        is_valid, error_msg = SecurityValidator.validate_phone_advanced(phone.strip())
        if not is_valid:
            log_security_event('phone_validation_failed', {
                'phone': phone[:20] + '...' if len(phone) > 20 else phone,
                'error': error_msg
            })
        return is_valid, error_msg

    def get_available_categories(self):
        """Получить список доступных категорий"""
        categories = ClubCategory.objects.filter(is_active=True)
        return [(cat.name.lower(), cat) for cat in categories]

    def find_category_by_name(self, category_name):
        """Найти категорию по названию"""
        try:
            return ClubCategory.objects.filter(
                is_active=True,
                name__iexact=category_name.strip()
            ).first()
        except:
            return None

    def process_message(self, session_id, message):
        """Основной метод обработки сообщения с защитой безопасности"""
        # 🔐 БЕЗОПАСНОСТЬ: Валидация и очистка входных данных
        if not message or not message.strip():
            return {
                'success': False,
                'message': '❌Сообщение не может быть пустым',
                'stage': 'error',
                'session_id': session_id
            }

        # Очищаем сообщение от потенциально опасного кода
        try:
            clean_message = sanitize_user_input(message.strip())
        except Exception as e:
            log_security_event('sanitization_failed', {
                'session_id': session_id,
                'error': str(e),
                'message_length': len(message) if message else 0
            })
            return {
                'success': False,
                'message': '❌Ошибка обработки сообщения',
                'stage': 'error',
                'session_id': session_id
            }

        # Дополнительная валидация контента
        is_valid, error_msg = validate_user_message(clean_message)
        if not is_valid:
            log_security_event('content_validation_failed', {
                'session_id': session_id,
                'error': error_msg,
                'message_preview': clean_message[:100] if clean_message else ''
            })
            return {
                'success': False,
                'message': f'❌{error_msg}',
                'stage': 'error',
                'session_id': session_id
            }

        # 🔧 ПЕРСИСТЕНТНОСТЬ: Получаем состояние из базы данных
        state = self.get_session_state(session_id)
        stage = state.stage
        club_data = state.data

        # Сначала проверяем специальные команды
        if clean_message.lower() in ['отмена', 'cancel', 'стоп']:
            return self.cancel_creation(session_id)

        if clean_message.lower() in ['помощь', 'help']:
            return self.show_help(stage)

        # Обрабатываем в зависимости от этапа
        if stage == 'welcome':
            return self.handle_welcome(session_id, clean_message)
        elif stage == 'name':
            return self.handle_name(session_id, clean_message)
        elif stage == 'category':
            return self.handle_category(session_id, clean_message)
        elif stage == 'description':
            return self.handle_description(session_id, clean_message)
        elif stage == 'email':
            return self.handle_email(session_id, clean_message)
        elif stage == 'phone':
            return self.handle_phone(session_id, clean_message)
        elif stage == 'confirm':
            return self.handle_confirmation(session_id, clean_message)

        return {
            'success': True,
            'message': 'Произошла ошибка. Давайте начнем сначала. Напишите "создать клуб"',
            'stage': 'welcome',
            'session_id': session_id
        }

    def handle_welcome(self, session_id, message):
        """Обработка приветственного этапа"""
        if any(keyword in message.lower() for keyword in ['создать клуб', 'создание клуба', 'новый клуб', 'хочу создать клуб']):
            # 🔧 ПЕРСИСТЕНТНОСТЬ: Обновляем состояние в базе данных
            updated_state = self._update_session_state(
                session_id=session_id,
                stage='name',
                last_question='name'
            )

            return {
                'success': True,
                'message': '''Отлично! Давайте создадим ваш клуб.

📝 **Шаг 1 из 6: Название клуба**

Как назовем ваш клуб? Придумайте интересное и запоминающееся название.''',
                'stage': updated_state.stage,
                'session_id': session_id,
                'progress': updated_state.progress
            }

        return {
            'success': True,
            'message': '''Я помогу вам создать клуб! 👥

Чтобы начать, напишите "создать клуб" или "хочу создать клуб"

Я задам вам несколько вопросов:
1. Название клуба
2. Категория
3. Описание
4. Email для связи
5. Телефон для связи

В любой момент можете написать "отмена" для отмены или "помощь" для подсказок.''',
            'stage': 'welcome',
            'session_id': session_id
        }

    def handle_name(self, session_id, message):
        """Обработка названия клуба"""
        name = message.strip()

        if len(name) < 3:
            return {
                'success': True,
                'message': '❌ Слишком короткое название. Название должно содержать минимум 3 символа.\n\nКак назовем ваш клуб?',
                'stage': 'name',
                'session_id': session_id
            }

        if len(name) > 100:
            return {
                'success': True,
                'message': '❌ Слишком длинное название. Название должно содержать максимум 100 символов.\n\nКак назовем ваш клуб?',
                'stage': 'name',
                'session_id': session_id
            }

        # Проверяем, что название уникальное
        if Club.objects.filter(name=name, is_active=True).exists():
            return {
                'success': True,
                'message': f'❌ Клуб с названием "{name}" уже существует. Придумайте другое название.\n\nКак назовем ваш клуб?',
                'stage': 'name',
                'session_id': session_id
            }

        # 🔧 ПЕРСИСТЕНТНОСТЬ: Сохраняем название в базе данных
        updated_state = self._update_session_state(
            session_id=session_id,
            stage='category',
            data_updates={'name': name},
            last_question='category'
        )

        # Получаем доступные категории
        categories = ClubCategory.objects.filter(is_active=True)
        category_list = '\n'.join([f"• {cat.name}" for cat in categories[:10]])

        return {
            'success': True,
            'message': f'''✅ Отлично! Клуб будет называться: **{name}**

📝 **Шаг 2 из 6: Категория клуба**

Выберите категорию из доступных:

{category_list}

Напишите название категории, которая лучше всего подходит вашему клубу.''',
            'stage': updated_state.stage,
            'session_id': session_id,
            'progress': updated_state.progress,
            'club_data': updated_state.data
        }

    def handle_category(self, session_id, message):
        """Обработка категории"""
        state = self.get_session_state(session_id)
        category_input = message.strip().lower()

        # Ищем категорию
        category = self.find_category_by_name(category_input)

        if not category:
            # Пробуем найти по ключевым словам
            categories = ClubCategory.objects.filter(is_active=True)
            found = False

            for cat in categories:
                if any(keyword in cat.name.lower() for keyword in category_input.split()):
                    category = cat
                    found = True
                    break

            if not found:
                available_categories = '\n'.join([f"• {cat.name}" for cat in categories])
                return {
                    'success': True,
                    'message': f'''❌ Категория "{message}" не найдена.

Доступные категории:
{available_categories}

Пожалуйста, выберите из списка или напишите похожее название.''',
                    'stage': 'category',
                    'session_id': session_id
                }

        # 🔧 ПЕРСИСТЕНТНОСТЬ: Сохраняем категорию в базе данных
        updated_state = self._update_session_state(
            session_id=session_id,
            stage='description',
            data_updates={
                'category': str(category.id),  # Сохраняем ID как строку для JSON
                'category_name': category.name
            },
            last_question='description'
        )

        return {
            'success': True,
            'message': f'''✅ Отлично! Категория: **{category.name}**

📝 **Шаг 3 из 6: Описание клуба**

Напишите подробное описание вашего клуба (минимум 200 символов).

Расскажите:
• Чем занимается ваш клуб
• Для кого он предназначен
• Какие мероприятия проводит
• Какие цели преследует

Пример описания:
"Наш клуб объединяет любителей бега в городе. Мы проводим утренние пробежки, участвуем в марафонах и делимся опытом. Вступайте к нам, если хотите вести здоровый образ жизни!"''',
            'stage': updated_state.stage,
            'session_id': session_id,
            'progress': updated_state.progress,
            'club_data': updated_state.data
        }

    def handle_description(self, session_id, message):
        """Обработка описания"""
        description = message.strip()

        if len(description) < 200:
            remaining = 200 - len(description)
            return {
                'success': True,
                'message': f'❌ Слишком короткое описание. Нужно минимум 200 символов.\n\nНапишите еще {remaining} символов:\n\nТекущий текст: "{description}"',
                'stage': 'description',
                'session_id': session_id
            }

        if len(description) > 2000:
            return {
                'success': True,
                'message': '❌ Слишком длинное описание. Максимум 2000 символов.\n\nНапишите более краткое описание:',
                'stage': 'description',
                'session_id': session_id
            }

        # 🔧 ПЕРСИСТЕНТНОСТЬ: Сохраняем описание в базе данных
        updated_state = self._update_session_state(
            session_id=session_id,
            stage='email',
            data_updates={'description': description},
            last_question='email'
        )

        return {
            'success': True,
            'message': f'''✅ Отлично! Описание добавлено.

📝 **Шаг 4 из 6: Email для связи**

Укажите email, по которому с вами смогут связываться участники клуба.

Пример: club@example.com''',
            'stage': updated_state.stage,
            'session_id': session_id,
            'progress': updated_state.progress,
            'club_data': updated_state.data
        }

    def handle_email(self, session_id, message):
        """Обработка email"""
        state = self.get_session_state(session_id)

        # Ищем email в сообщении
        email = self.extract_email(message)

        if not email:
            # Пробуем взять всё сообщение как email
            email = message.strip()

        # 🔐 Улучшенная валидация email
        is_valid, error_msg = self.validate_email(email)
        if not is_valid:
            return {
                'success': True,
                'message': f'''❌ Некорректный email: "{email}"

{error_msg}

Пример: club@example.com или info@myclub.kz''',
                'stage': 'email',
                'session_id': session_id
            }

        # 🔧 ПЕРСИСТЕНТНОСТЬ: Сохраняем email в базе данных
        updated_state = self._update_session_state(
            session_id=session_id,
            stage='phone',
            data_updates={'email': email},
            last_question='phone'
        )

        return {
            'success': True,
            'message': f'''✅ Email добавлен: {email}

📝 **Шаг 5 из 6: Телефон для связи**

Укажите телефон для связи с участниками.

Пример: +7 701 234 5678 или 87771234567''',
            'stage': updated_state.stage,
            'session_id': session_id,
            'progress': updated_state.progress,
            'club_data': updated_state.data
        }

    def handle_phone(self, session_id, message):
        """Обработка телефона"""
        state = self.get_session_state(session_id)

        # Ищем телефон в сообщении
        phone = self.extract_phone(message)

        if not phone:
            # Пробуем взять всё сообщение как телефон
            phone = message.strip()

        # 🔐 Улучшенная валидация телефона
        is_valid, error_msg = self.validate_phone(phone)
        if not is_valid:
            return {
                'success': True,
                'message': f'''❌ Некорректный телефон: "{phone}"

{error_msg}

Примеры:
• +7 701 234 5678
• 8777 123 45 67
• 7012345678''',
                'stage': 'phone',
                'session_id': session_id
            }

        # 🔧 ПЕРСИСТЕНТНОСТЬ: Сохраняем телефон в базе данных
        updated_state = self._update_session_state(
            session_id=session_id,
            stage='confirm',
            data_updates={'phone': phone},
            last_question='confirm'
        )

        # Показываем данные для подтверждения
        data = updated_state.data
        category_name = data.get('category_name', str(data.get('category', '')))

        confirmation_text = f'''
✅ **Проверьте данные клуба:**

🏷️ **Название:** {data.get('name', '')}
📂 **Категория:** {category_name}
📧 **Email:** {data.get('email', '')}
📱 **Телефон:** {data.get('phone', '')}
📝 **Описание:** {data.get('description', '')[:200]}...

Все правильно?

Напишите:
• **"да"** - для создания клуба
• **"нет"** - для внесения исправлений
• **"отмена"** - для отмены создания
'''

        return {
            'success': True,
            'message': confirmation_text,
            'stage': updated_state.stage,
            'session_id': session_id,
            'progress': updated_state.progress,
            'club_data': updated_state.data
        }

    def handle_confirmation(self, session_id, message):
        """Обработка подтверждения"""
        state = self.get_session_state(session_id)

        if message.lower() in ['да', 'yes', 'д', 'y']:
            return self.create_club(session_id)
        elif message.lower() in ['нет', 'no', 'н', 'n']:
            return self.edit_club_data(session_id)
        elif message.lower() in ['отмена', 'cancel']:
            return self.cancel_creation(session_id)
        else:
            return {
                'success': True,
                'message': '''❌ Непонятный ответ.

Напишите:
• **"да"** - чтобы создать клуб
• **"нет"** - чтобы внести исправления
• **"отмена"** - чтобы отменить создание''',
                'stage': 'confirm',
                'session_id': session_id
            }

    def edit_club_data(self, session_id):
        """Редактирование данных клуба"""
        return {
            'success': True,
            'message': '''📝 **Что хотите исправить?**

Напишите:
• **"название"** - изменить название
• **"категория"** - изменить категорию
• **"описание"** - изменить описание
• **"email"** - изменить email
• **"телефон"** - изменить телефон
• **"отмена"** - отменить создание''',
            'stage': 'edit',
            'session_id': session_id
        }

    def create_club(self, session_id):
        """Создание клуба в базе данных с использованием персистентных сервисов"""
        try:
            # 🔧 ПЕРСИСТЕНТНОСТЬ: Получаем состояние из базы данных
            state = self.get_session_state(session_id)
            data = state.data

            # 🔧 ОТСЛЕЖИВАНИЕ: Начинаем отслеживание создания клуба (прямые операции с моделями)
            try:
                creation_request = ClubCreationRequest.objects.create(
                    session_state=state,
                    club_name=data.get('name', ''),
                    category=data.get('category_name', ''),
                    description=data.get('description', ''),
                    email=data.get('email', ''),
                    phone=data.get('phone', ''),
                    status='pending'
                )
                logger.info(f"Tracking club creation request: {data.get('name')} - {creation_request.id}")
            except Exception as e:
                logger.error(f"Failed to create ClubCreationRequest: {e}")
                creation_request = None

            # Ищем пользователя по умолчанию (для демо)
            from accounts.models import User
            default_user = User.objects.first()

            if not default_user:
                # Отмечаем ошибку создания
                if creation_request:
                    creation_request.status = 'failed'
                    creation_request.error_message = "Не удалось найти пользователя для создания клуба"
                    creation_request.save()
                return {
                    'success': False,
                    'message': '❌ Ошибка: невозможно найти пользователя для создания клуба. Обратитесь к администратору.',
                    'stage': 'error',
                    'session_id': session_id
                }

            # Ищем категорию (используем ID из сохраненных данных)
            from clubs.models import ClubCategory
            try:
                category_id = data.get('category')
                if category_id:
                    category = ClubCategory.objects.get(id=category_id)
                else:
                    # Fallback к поиску по имени
                    category = ClubCategory.objects.get(name=data.get('category_name', ''))
            except (ClubCategory.DoesNotExist, ValueError):
                # Если категория не найдена, используем первую доступную
                category = ClubCategory.objects.first()
                if not category:
                    # Отмечаем ошибку создания
                    if creation_request:
                        creation_request.status = 'failed'
                        creation_request.error_message = "Не удалось найти категорию для клуба"
                        creation_request.save()
                    return {
                        'success': False,
                        'message': '❌ Ошибка: невозможно найти категорию для клуба. Обратитесь к администратору.',
                        'stage': 'error',
                        'session_id': session_id
                    }

            # Создаем клуб
            club = Club.objects.create(
                name=data.get('name'),
                category=category,
                creater=default_user,
                description=data.get('description'),
                email=data.get('email'),
                phone=data.get('phone'),
                members_count=1
            )

            # Добавляем создателя в участники
            club.members.add(default_user)

            # 🔧 УСПЕХ: Отмечаем успешное создание
            if creation_request:
                creation_request.status = 'success'
                creation_request.club_id = str(club.id)
                creation_request.save()
                logger.info(f"Club creation successful: {data.get('name')} - {club.id}")

            # 🔧 ПЕРСИСТЕНТНОСТЬ: Обновляем состояние как завершенное (прямая операция)
            try:
                from django.db import transaction
                with transaction.atomic():
                    state = ConversationState.objects.get(session_id=session_id)
                    state.stage = 'done'
                    state.save()
                    logger.info(f"Session {session_id} marked as completed")
            except Exception as e:
                logger.warning(f"Failed to update session state: {e}")

            return {
                'success': True,
                'message': f'''🎉 **Клуб успешно создан!**

🏷️ **Название:** {club.name}
📂 **Категория:** {club.category.name}
🆔 **ID клуба:** {club.id}

Ваш клуб теперь доступен на платформе! Пользователи могут находить его и вступать.

Спасибо, что воспользовались ИИ-консультантом для создания клуба! 🚀''',
                'stage': 'done',
                'session_id': session_id,
                'club_id': str(club.id),
                'club_created': True
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'❌ Произошла ошибка при создании клуба: {str(e)}',
                'stage': 'error',
                'session_id': session_id
            }

    def cancel_creation(self, session_id):
        """Отмена создания клуба с использованием персистентных сервисов"""
        # 🔧 ПЕРСИСТЕНТНОСТЬ: Удаляем состояние из базы данных (прямая операция)
        try:
            state = ConversationState.objects.get(session_id=session_id)
            state.delete()
            logger.info(f"Session {session_id} deleted")
        except ConversationState.DoesNotExist:
            pass  # Сессия уже не существует, это не ошибка
        except Exception as e:
            logger.warning(f"Failed to delete session {session_id}: {e}")

        return {
            'success': True,
            'message': '❌ Создание клуба отменено.\n\nЕсли захотите создать клуб позже, просто напишите "создать клуб"',
            'stage': 'welcome',
            'session_id': session_id,
            'cancelled': True
        }

    def show_help(self, current_stage):
        """Показать помощь для текущего этапа"""
        help_messages = {
            'welcome': 'Чтобы начать создание клуба, напишите "создать клуб"',
            'name': 'Придумайте уникальное название для вашего клуба (3-100 символов)',
            'category': 'Выберите категорию, которая лучше всего описывает ваш клуб',
            'description': 'Напишите подробное описание (минимум 200 символов) о том, чем занимается ваш клуб',
            'email': 'Укажите email для связи с участниками клуба',
            'phone': 'Укажите номер телефона (10-15 цифр) для связи',
            'confirm': 'Проверьте все данные и напишите "да" для создания клуба или "нет" для исправлений'
        }

        help_text = help_messages.get(current_stage, 'Напишите "помощь" на нужном этапе')

        return {
            'success': True,
            'message': f'💡 **Подсказка:**\n\n{help_text}',
            'stage': current_stage,
            'help_shown': True
        }

# 🏗️ DEPENDENCY INJECTION - Убираем глобальный экземпляр
# Вместо глобального club_creator будем использовать DI контейнер

def get_club_creator():
    """Получить экземпляр AIClubCreator из DI контейнера"""
    try:
        from ai_consultant.di_container import get_service
        return get_service('club_creator')
    except Exception:
        # Fallback на прямое создание, если DI недоступен
        logger.warning("DI container not available, falling back to direct instantiation")
        return AIClubCreator()

@csrf_exempt
@require_http_methods(["GET", "POST"])
@sensitive_post_parameters()
def ai_club_creator_public(request):
    """
    Интерактивный создатель клубов через ИИ консультанта
    """
    if request.method == 'GET':
        return JsonResponse({
            'message': 'AI Club Creator - Interactive Club Creation',
            'description': 'Создавайте клубы через диалог с ИИ консультантом',
            'how_to_use': [
                'POST /api/v1/ai/club-creator/',
                '{"message": "создать клуб", "session_id": "unique_id"}'
            ],
            'stages': [
                'welcome - Начало создания',
                'name - Название клуба',
                'category - Категория',
                'description - Описание',
                'email - Email для связи',
                'phone - Телефон',
                'confirm - Подтверждение'
            ],
            'status': 'ready',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

    if request.method == 'POST':
        try:
            # Получаем данные из request
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST.dict()

            message = data.get('message', '').strip()
            session_id = data.get('session_id') or str(uuid.uuid4())

            if not message:
                return JsonResponse({
                    'error': 'Message is required',
                    'success': False
                }, status=400)

            # 🏗️ DEPENDENCY INJECTION: Получаем club_creator из DI контейнера
            club_creator_instance = get_club_creator()

            # 🔧 ЛОГИРОВАНИЕ: Логируем ввод пользователя (временно отключено)
            # TODO: Восстановить логирование после рефакторинга сервисов
            # try:
            #     session_logging_service.log_user_input(
            #         session_id=session_id,
            #         message=message,
            #         ip_address=request.META.get('REMOTE_ADDR'),
            #         user_agent=request.META.get('HTTP_USER_AGENT'),
            #         stage=getattr(club_creator_instance.get_session_state(session_id), 'stage', 'unknown')
            #     )
            # except Exception as e:
            #     logger.warning(f"Logging failed: {e}")

            # Обрабатываем сообщение через ИИ создателя клубов
            import time
            start_time = time.time()
            result = club_creator_instance.process_message(session_id, message)
            processing_time = time.time() - start_time

            # 🔧 ЛОГИРОВАНИЕ: Логируем ответ ИИ (временно отключено)
            # TODO: Восстановить логирование после рефакторинга сервисов
            # try:
            #     session_logging_service.log_ai_response(
            #         session_id=session_id,
            #         response_data=result,
            #         processing_time=processing_time,
            #         stage=result.get('stage', 'unknown'),
            #         ip_address=request.META.get('REMOTE_ADDR')
            #     )
            # except Exception as e:
            #     logger.warning(f"Logging failed: {e}")

            # 🔐 БЕЗОПАСНОСТЬ: Очищаем AI ответ перед отправкой пользователю
            if result.get('success') and 'message' in result:
                try:
                    result['message'] = SecurityValidator.sanitize_ai_response(result['message'])
                except Exception as e:
                    log_security_event('ai_response_sanitization_failed', {
                        'session_id': session_id,
                        'error': str(e)
                    })
                    # Fallback - базовое экранирование
                    result['message'] = html.escape(result['message'])

            # Создаем копию результата для сериализации
            serializable_result = result.copy()

            # Убираем не-сериализуемые объекты
            if 'club_data' in serializable_result and isinstance(serializable_result['club_data'], dict):
                club_data = serializable_result['club_data']
                if 'category' in club_data and hasattr(club_data['category'], 'name'):
                    club_data['category'] = club_data['category'].name

            # 🔐 БЕЗОПАСНОСТЬ: Дополнительная очистка всех текстовых полей
            for key, value in serializable_result.items():
                if isinstance(value, str) and key != 'error':  # Не очищаем сообщения об ошибках
                    try:
                        serializable_result[key] = SecurityValidator.sanitize_ai_response(value)
                    except Exception:
                        serializable_result[key] = html.escape(value)

            # Добавляем техническую информацию
            serializable_result.update({
                'session_id': session_id,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'processing_mode': 'ai_club_creator'
            })

            return JsonResponse(serializable_result)

        except json.JSONDecodeError as e:
            # 🔧 ЛОГИРОВАНИЕ: Временно отключено
            # TODO: Восстановить после рефакторинга сервисов
            logger.error(f"JSON decode error: {str(e)}")
            return JsonResponse({
                'error': 'Invalid JSON data',
                'success': False
            }, status=400)
        except Exception as e:
            # 🔧 ЛОГИРОВАНИЕ: Временно отключено
            # TODO: Восстановить после рефакторинга сервисов
            logger.error(f"Internal server error: {str(e)}")
            return JsonResponse({
                'error': f'Internal error: {str(e)}',
                'success': False
            }, status=500)