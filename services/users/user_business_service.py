"""
User Business Service
Вынесенная бизнес-логика из accounts/api/views.py
"""

import logging
from typing import Dict, Any, Optional, Tuple
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.core.cache import cache
from rest_framework import status

User = get_user_model()
logger = logging.getLogger(__name__)


class UserValidator:
    """Валидатор данных пользователя"""

    @staticmethod
    def validate_phone_number(phone: str) -> str:
        """
        Валидация номера телефона
        """
        if not phone:
            raise ValidationError("Номер телефона обязателен")

        # Очистка номера
        phone = ''.join(filter(str.isdigit, phone))

        if len(phone) < 10:
            raise ValidationError("Номер телефона слишком короткий")

        if len(phone) > 15:
            raise ValidationError("Номер телефона слишком длинный")

        return phone

    @staticmethod
    def validate_user_creation_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Валидация данных для создания пользователя
        """
        validated_data = {}

        # Валидация username
        username = data.get('username', '').strip()
        if not username:
            raise ValidationError("Имя пользователя обязательно")
        if len(username) < 3:
            raise ValidationError("Имя пользователя слишком короткое")
        if User.objects.filter(username=username).exists():
            raise ValidationError("Пользователь с таким именем уже существует")
        validated_data['username'] = username

        # Валидация email
        email = data.get('email', '').strip().lower()
        if email and User.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с таким email уже существует")
        validated_data['email'] = email or ''

        # Валидация телефона
        phone = data.get('phone', '').strip()
        validated_data['phone'] = UserValidator.validate_phone_number(phone)

        # Валидация имени
        first_name = data.get('first_name', '').strip()
        validated_data['first_name'] = first_name or ''

        # Валидация фамилии
        last_name = data.get('last_name', '').strip()
        validated_data['last_name'] = last_name or ''

        return validated_data


class UserBusinessService:
    """
    Бизнес-логика для управления пользователями
    """

    def __init__(self):
        self.validator = UserValidator()
        self.cache_timeout = 300  # 5 минут

    def create_user_with_session(self, user_data: Dict[str, Any],
                                session_key: str = None) -> Tuple[Dict[str, Any], int]:
        """
        Создание пользователя с сессией

        Returns:
            Tuple[response_data, status_code]
        """
        try:
            with transaction.atomic():
                # Валидация данных
                validated_data = self.validator.validate_user_creation_data(user_data)

                # Установка пароля, если не предоставлен
                password = user_data.get('password')
                if not password:
                    # Генерация временного пароля
                    password = User.objects.make_random_password(length=8)

                # Создание пользователя
                user = User.objects.create_user(
                    username=validated_data['username'],
                    email=validated_data['email'],
                    phone=validated_data['phone'],
                    first_name=validated_data['first_name'],
                    last_name=validated_data['last_name'],
                    password=password,
                    is_active=True
                )

                # Создание или обновление сессии
                if session_key:
                    self._update_user_session(session_key, user)

                # Очистка кэша пользователя
                self._clear_user_cache(user.id)

                logger.info(f"User created: {user.id} with username: {user.username}")

                response_data = {
                    'user_id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'phone': user.phone,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'created_at': user.created_at.isoformat(),
                    'is_active': user.is_active,
                    'session_key': session_key
                }

                # Добавляем временный пароль только если он был сгенерирован
                if not user_data.get('password'):
                    response_data['temp_password'] = password

                return response_data, status.HTTP_201_CREATED

        except ValidationError as e:
            logger.warning(f"Validation error creating user: {e}")
            return self._format_error_response(str(e), status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return self._format_error_response(
                "Ошибка при создании пользователя",
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update_user_profile(self, user_id: int, update_data: Dict[str, Any],
                           requesting_user: User = None) -> Tuple[Dict[str, Any], int]:
        """
        Обновление профиля пользователя

        Returns:
            Tuple[response_data, status_code]
        """
        try:
            # Проверка прав доступа
            if requesting_user and requesting_user.id != user_id and not requesting_user.is_staff:
                return self._format_error_response(
                    "Доступ запрещен",
                    status.HTTP_403_FORBIDDEN
                )

            # Получение пользователя
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return self._format_error_response(
                    "Пользователь не найден",
                    status.HTTP_404_NOT_FOUND
                )

            with transaction.atomic():
                # Валидация и обновление полей
                update_fields = []

                # Email
                if 'email' in update_data:
                    email = update_data['email'].strip().lower()
                    if email and email != user.email:
                        if User.objects.filter(email=email).exclude(id=user_id).exists():
                            raise ValidationError("Пользователь с таким email уже существует")
                        user.email = email
                        update_fields.append('email')

                # Телефон
                if 'phone' in update_data:
                    phone = self.validator.validate_phone_number(update_data['phone'])
                    if phone != user.phone:
                        if User.objects.filter(phone=phone).exclude(id=user_id).exists():
                            raise ValidationError("Пользователь с таким телефоном уже существует")
                        user.phone = phone
                        update_fields.append('phone')

                # Имя
                if 'first_name' in update_data:
                    first_name = update_data['first_name'].strip()
                    if first_name != user.first_name:
                        user.first_name = first_name
                        update_fields.append('first_name')

                # Фамилия
                if 'last_name' in update_data:
                    last_name = update_data['last_name'].strip()
                    if last_name != user.last_name:
                        user.last_name = last_name
                        update_fields.append('last_name')

                # Username (только для админа)
                if 'username' in update_data and (requesting_user and requesting_user.is_staff):
                    username = update_data['username'].strip()
                    if username != user.username:
                        if User.objects.filter(username=username).exclude(id=user_id).exists():
                            raise ValidationError("Пользователь с таким именем уже существует")
                        user.username = username
                        update_fields.append('username')

                # Сохранение изменений
                if update_fields:
                    user.save(update_fields=update_fields)

                    # Очистка кэша
                    self._clear_user_cache(user_id)

                logger.info(f"User profile updated: {user_id}")

                response_data = {
                    'user_id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'phone': user.phone,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'updated_at': user.updated_at.isoformat() if user.updated_at else None
                }

                return response_data, status.HTTP_200_OK

        except ValidationError as e:
            logger.warning(f"Validation error updating user {user_id}: {e}")
            return self._format_error_response(str(e), status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            return self._format_error_response(
                "Ошибка при обновлении профиля",
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_user_profile(self, user_id: int, requesting_user: User = None) -> Tuple[Dict[str, Any], int]:
        """
        Получение профиля пользователя

        Returns:
            Tuple[response_data, status_code]
        """
        try:
            # Проверка прав доступа
            if requesting_user and requesting_user.id != user_id and not requesting_user.is_staff:
                return self._format_error_response(
                    "Доступ запрещен",
                    status.HTTP_403_FORBIDDEN
                )

            # Попытка получить из кэша
            cache_key = f"user_profile_{user_id}"
            cached_profile = cache.get(cache_key)
            if cached_profile:
                return cached_profile, status.HTTP_200_OK

            # Получение пользователя
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return self._format_error_response(
                    "Пользователь не найден",
                    status.HTTP_404_NOT_FOUND
                )

            profile_data = {
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'phone': user.phone,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_active': user.is_active,
                'is_staff': user.is_staff,
                'date_joined': user.date_joined.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None
            }

            # Кэширование результата
            cache.set(cache_key, profile_data, self.cache_timeout)

            return profile_data, status.HTTP_200_OK

        except Exception as e:
            logger.error(f"Error getting user profile {user_id}: {e}")
            return self._format_error_response(
                "Ошибка при получении профиля",
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def deactivate_user(self, user_id: int, requesting_user: User = None) -> Tuple[Dict[str, Any], int]:
        """
        Деактивация пользователя

        Returns:
            Tuple[response_data, status_code]
        """
        try:
            # Проверка прав доступа
            if not requesting_user or (requesting_user.id != user_id and not requesting_user.is_staff):
                return self._format_error_response(
                    "Доступ запрещен",
                    status.HTTP_403_FORBIDDEN
                )

            # Получение пользователя
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return self._format_error_response(
                    "Пользователь не найден",
                    status.HTTP_404_NOT_FOUND
                )

            # Деактивация
            user.is_active = False
            user.save(update_fields=['is_active'])

            # Очистка кэша
            self._clear_user_cache(user_id)

            logger.info(f"User deactivated: {user_id}")

            return {'message': 'Пользователь деактивирован'}, status.HTTP_200_OK

        except Exception as e:
            logger.error(f"Error deactivating user {user_id}: {e}")
            return self._format_error_response(
                "Ошибка при деактивации пользователя",
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # Вспомогательные методы

    def _update_user_session(self, session_key: str, user: User):
        """Обновление сессии пользователя"""
        try:
            from django.contrib.sessions.models import Session
            from django.contrib.sessions.backends.db import SessionStore

            session = SessionStore(session_key=session_key)
            session['user_id'] = user.id
            session.save()
        except Exception as e:
            logger.warning(f"Failed to update user session: {e}")

    def _clear_user_cache(self, user_id: int):
        """Очистка кэша пользователя"""
        try:
            cache_keys = [
                f"user_profile_{user_id}",
                f"user_data_{user_id}",
            ]
            cache.delete_many(cache_keys)
        except Exception as e:
            logger.warning(f"Failed to clear user cache: {e}")

    def _format_error_response(self, error_message: str, status_code: int) -> Tuple[Dict[str, Any], int]:
        """Формирование ответа с ошибкой"""
        return {
            'error': error_message,
            'timestamp': timezone.now().isoformat()
        }, status_code


# Глобальный экземпляр сервиса
user_business_service = UserBusinessService()