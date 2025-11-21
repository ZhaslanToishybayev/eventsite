"""
📝 Контекст сервис v2.0
Управление системным контекстом и настройками ИИ
"""

import logging
from typing import Dict, List, Optional, Any
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.db import transaction

from ..models import AIContext
from .base import BaseAIService

User = get_user_model()
logger = logging.getLogger(__name__)


class ContextService(BaseAIService):
    """
    Сервис для управления контекстом ИИ-ассистента
    """

    def __init__(self):
        super().__init__()
        self.default_contexts = self._get_default_contexts()
        self.cache_timeout = 3600  # 1 час

    def process(self, category: str, content: str, **kwargs) -> bool:
        """
        Основной метод обновления контекста
        """
        return self.update_context(category, content, **kwargs)

    def get_system_context(self) -> str:
        """
        Получает основной системный контекст
        """
        try:
            cache_key = "system_context_primary"
            cached_context = cache.get(cache_key)

            if cached_context:
                self.log_info("Системный контекст загружен из кэша")
                return cached_context

            # Получаем активные системные контексты
            contexts = AIContext.objects.filter(
                category='system',
                is_active=True
            ).order_by('created_at')

            if contexts.exists():
                context_text = "\n\n".join([
                    f"📌 {ctx.key}:\n{ctx.content}"
                    for ctx in contexts
                ])
            else:
                # Используем контекст по умолчанию
                context_text = self.default_contexts.get('system', '')

            # Кэшируем результат
            cache.set(cache_key, context_text, self.cache_timeout)

            self.log_info(f"Системный контекст загружен", {
                'contexts_count': contexts.count(),
                'length': len(context_text)
            })

            return context_text

        except Exception as e:
            self.log_error(f"Ошибка получения системного контекста: {e}")
            return self.default_contexts.get('system', '')

    def get_context_by_category(self, category: str) -> str:
        """
        Получает контекст по категории
        """
        try:
            cache_key = f"context_category_{category}"
            cached_context = cache.get(cache_key)

            if cached_context:
                return cached_context

            context = AIContext.objects.filter(
                category=category,
                is_active=True
            ).first()

            if context:
                result = context.content
            else:
                result = self.default_contexts.get(category, '')

            cache.set(cache_key, result, self.cache_timeout)
            return result

        except Exception as e:
            self.log_error(f"Ошибка получения контекста категории {category}: {e}")
            return self.default_contexts.get(category, '')

    def update_context(self, category: str, content: str, is_active: bool = True,
                      title: str = None, priority: int = 1) -> bool:
        """
        Обновляет или создает контекст
        """
        try:
            with transaction.atomic():
                context, created = AIContext.objects.update_or_create(
                    category=category,
                    defaults={
                        'title': title or f"Контекст {category}",
                        'content': content,
                        'is_active': is_active,
                        'priority': priority
                    }
                )

                # Очищаем кэш
                self._clear_context_cache(category)

                self.log_info(f"Контекст {'создан' if created else 'обновлен'}", {
                    'category': category,
                    'context_id': context.id,
                    'active': is_active
                })

                return True

        except Exception as e:
            self.log_error(f"Ошибка обновления контекста {category}: {e}")
            return False

    def create_context(self, category: str, title: str, content: str,
                      priority: int = 1, is_active: bool = True) -> Optional[AIContext]:
        """
        Создает новый контекст
        """
        try:
            context = AIContext.objects.create(
                category=category,
                title=title,
                content=content,
                priority=priority,
                is_active=is_active
            )

            # Очищаем кэш
            self._clear_context_cache(category)

            self.log_info(f"Контекст создан", {
                'category': category,
                'context_id': context.id,
                'title': title
            })

            return context

        except Exception as e:
            self.log_error(f"Ошибка создания контекста: {e}")
            return None

    def delete_context(self, context_id: int) -> bool:
        """
        Удаляет контекст
        """
        try:
            context = AIContext.objects.get(id=context_id)
            category = context.category
            context.delete()

            # Очищаем кэш
            self._clear_context_cache(category)

            self.log_info(f"Контекст удален", {
                'context_id': context_id,
                'category': category
            })

            return True

        except AIContext.DoesNotExist:
            self.log_error(f"Контекст с id {context_id} не найден")
            return False
        except Exception as e:
            self.log_error(f"Ошибка удаления контекста: {e}")
            return False

    def get_all_contexts(self, category: str = None) -> List[Dict[str, Any]]:
        """
        Получает все контексты (опционально фильтруя по категории)
        """
        try:
            query = AIContext.objects.all()
            if category:
                query = query.filter(category=category)

            contexts = query.order_by('category', 'priority', 'created_at')

            result = []
            for ctx in contexts:
                result.append({
                    'id': ctx.id,
                    'category': ctx.category,
                    'title': ctx.title,
                    'content': ctx.content,
                    'priority': ctx.priority,
                    'is_active': ctx.is_active,
                    'created_at': ctx.created_at.isoformat(),
                    'updated_at': ctx.updated_at.isoformat()
                })

            self.log_info(f"Контексты загружены", {
                'category': category or 'all',
                'count': len(result)
            })

            return result

        except Exception as e:
            self.log_error(f"Ошибка получения контекстов: {e}")
            return []

    def toggle_context(self, context_id: int) -> bool:
        """
        Переключает активность контекста
        """
        try:
            context = AIContext.objects.get(id=context_id)
            context.is_active = not context.is_active
            context.save(update_fields=['is_active'])

            # Очищаем кэш
            self._clear_context_cache(context.category)

            self.log_info(f"Активность контекста переключена", {
                'context_id': context_id,
                'is_active': context.is_active
            })

            return True

        except AIContext.DoesNotExist:
            self.log_error(f"Контекст с id {context_id} не найден")
            return False
        except Exception as e:
            self.log_error(f"Ошибка переключения контекста: {e}")
            return False

    def get_personalized_context(self, user: User) -> str:
        """
        Получает персонализированный контекст для пользователя
        """
        try:
            base_context = self.get_system_context()

            # Добавляем информацию о пользователе
            user_context = f"\n\n👤 Информация о пользователе:\n"
            user_context += f"- ID: {user.id}\n"
            user_context += f"- Username: {user.username}\n"

            if hasattr(user, 'profile'):
                profile = user.profile
                if profile.interests:
                    user_context += f"- Интересы: {profile.interests}\n"
                if profile.bio:
                    user_context += f"- О себе: {profile.bio}\n"

            # Получаем историю пользователя для контекста
            from django.db.models import Count
            from ..models import ChatSession

            user_sessions = ChatSession.objects.filter(user=user, is_active=True)
            total_messages = ChatSession.objects.filter(id__in=user_sessions).aggregate(
                total=Count('messages')
            )['total'] or 0

            user_context += f"- Всего сообщений в чате: {total_messages}\n"

            return base_context + user_context

        except Exception as e:
            self.log_error(f"Ошибка получения персонализированного контекста: {e}")
            return self.get_system_context()

    def reset_to_defaults(self, category: str = None) -> bool:
        """
        Сбрасывает контексты к значениям по умолчанию
        """
        try:
            if category:
                # Сбрасываем только указанную категорорию
                AIContext.objects.filter(category=category).delete()
                default_content = self.default_contexts.get(category, '')
                if default_content:
                    self.create_context(
                        category=category,
                        title=f"Контекст {category} по умолчанию",
                        content=default_content
                    )
            else:
                # Сбрасываем все категории
                AIContext.objects.all().delete()
                for cat, content in self.default_contexts.items():
                    self.create_context(
                        category=cat,
                        title=f"Контекст {cat} по умолчанию",
                        content=content
                    )

            # Очищаем весь кэш
            cache.delete_many([f"context_{key}" for key in cache.keys("context_*")])

            self.log_info(f"Контексты сброшены к умолчаниям", {'category': category or 'all'})
            return True

        except Exception as e:
            self.log_error(f"Ошибка сброса контекстов: {e}")
            return False

    def _get_default_contexts(self) -> Dict[str, str]:
        """
        Возвращает контексты по умолчанию
        """
        return {
            'system': """🤖 Ты - ИИ-ассистент платформы UnitySphere.

Твои задачи:
- Помогать пользователям изучать платформу
- Отвечать на вопросы о функциях UnitySphere
- Помогать создавать клубы и находить единомышленников
- Предлагать идеи для развития и сотрудничества

Стиль общения:
- Дружелюбный и профессиональный
- Структурированные ответы с эмодзи
- Краткие и ёмкие ответы
- Всегда предлагай дополнительные действия

Правила:
- Не разглашай чувствительную информацию
- Отвечай только в рамках тематики платформы
- При сложных вопросах предлагай обратиться к документации
- Используй русский язык""",

            'club_creation': """🎯 Создание клубов на UnitySphere:

Этапы создания клуба:
1. Определение тематики и аудитории
2. Разработка названия и описания
3. Создание правил и структуры
4. Привлечение первых участников
5. Организация мероприятий

Популярные темы клубов:
- Профессиональные сообщества
- Хобби и увлечения
- Образование и развитие
- Спорт и здоровье
- Искусство и творчество
- Технологии и инновации

Всегда помогай пользователям с конкретными шагами!""",

            'user_support': """💬 Поддержка пользователей:

Основные разделы помощи:
- Регистрация и настройка профиля
- Поиск и вступление в клубы
- Создание собственного контента
- Общение и взаимодействие
- Решение технических проблем

При проблемах:
- Определи суть вопроса
- Предложи конкретное решение
- Дай пошаговую инструкцию
- Предложи альтернативные варианты

Всегда будь вежлив и терпелив!"""
        }

    def _clear_context_cache(self, category: str = None):
        """
        Очищает кэш контекстов
        """
        try:
            if category:
                cache.delete(f"context_category_{category}")
                cache.delete("system_context_primary")
            else:
                # Очищаем все контекстные ключи
                cache.delete_many([f"context_{key}" for key in cache.keys("context_*")])
        except Exception as e:
            self.log_error(f"Ошибка очистки кэша контекстов: {e}")

    def health_check(self) -> bool:
        """
        Проверка работоспособности сервиса
        """
        try:
            # Проверяем доступность БД
            AIContext.objects.count()
            return True
        except Exception as e:
            self.log_error(f"Health check не пройден: {e}")
            return False