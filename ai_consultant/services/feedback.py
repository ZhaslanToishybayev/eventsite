import json
from typing import List, Dict, Optional
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Q, Count, Avg
from ..models import FeedbackCategory, UserFeedback, FeedbackRating

User = get_user_model()


class FeedbackService:
    """
    Сервис для управления обратной связью
    """

    def __init__(self):
        self.categories = self._get_default_categories()

    def _get_default_categories(self) -> Dict[str, Dict]:
        """Возвращает категории обратной связи по умолчанию"""
        return {
            'general': {
                'name': 'Общая обратная связь',
                'description': 'Общие вопросы, предложения и комментарии',
                'icon': '💬',
                'color': '#007bff',
                'order': 1
            },
            'technical': {
                'name': 'Техническая поддержка',
                'description': 'Проблемы с сайтом, ошибки, баги',
                'icon': '🔧',
                'color': '#dc3545',
                'order': 2
            },
            'feature': {
                'name': 'Новые функции',
                'description': 'Предложения по улучшению и новые функции',
                'icon': '✨',
                'color': '#28a745',
                'order': 3
            },
            'content': {
                'name': 'Контент и информация',
                'description': 'Вопросы о контенте, информация о клубах',
                'icon': '📚',
                'color': '#17a2b8',
                'order': 4
            },
            'partnership': {
                'name': 'Сотрудничество',
                'description': 'Предложения о партнерстве и сотрудничестве',
                'icon': '🤝',
                'color': '#6f42c1',
                'order': 5
            },
            'complaint': {
                'name': 'Жалобы',
                'description': 'Жалобы на пользователей, контент или сервис',
                'icon': '⚠️',
                'color': '#fd7e14',
                'order': 6
            }
        }

    def initialize_categories(self):
        """Инициализирует категории обратной связи"""
        for category_key, category_data in self.categories.items():
            category, created = FeedbackCategory.objects.get_or_create(
                name=category_data['name'],
                defaults={
                    'description': category_data['description'],
                    'icon': category_data['icon'],
                    'color': category_data['color'],
                    'order': category_data['order']
                }
            )
            if created:
                print(f"✅ Создана категория: {category.name}")

    def create_feedback(self, data: Dict, user: Optional[User] = None) -> Dict:
        """
        Создает новое обращение обратной связи
        """
        try:
            # Получаем категорию
            category_name = data.get('category', 'Общая обратная связь')
            category = FeedbackCategory.objects.filter(name=category_name).first()

            if not category:
                category = FeedbackCategory.objects.filter(name='Общая обратная связь').first()
                if not category:
                    category = FeedbackCategory.objects.first()

            # Определяем приоритет на основе типа
            feedback_type = data.get('feedback_type', 'suggestion')
            priority = self._determine_priority(feedback_type, data.get('message', ''))

            # Создаем обращение
            feedback = UserFeedback.objects.create(
                user=user,
                category=category,
                feedback_type=feedback_type,
                title=data.get('title', '')[:200],
                message=data.get('message', ''),
                email=data.get('email', '') or (user.email if user else ''),
                phone=data.get('phone', ''),
                page_url=data.get('page_url', ''),
                user_agent=data.get('user_agent', ''),
                ip_address=data.get('ip_address', ''),
                priority=priority
            )

            return {
                'success': True,
                'feedback_id': str(feedback.id),
                'message': 'Ваше обращение успешно отправлено! Мы свяжемся с вами в ближайшее время.',
                'category': category.name,
                'priority': feedback.get_priority_display()
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'Произошла ошибка при отправке обращения: {str(e)}'
            }

    def _determine_priority(self, feedback_type: str, message: str) -> int:
        """Определяет приоритет обращения на основе типа и содержания"""
        high_priority_keywords = [
            'срочно', 'экстренно', 'критический', 'не работает', 'ошибка', 'проблема',
            'баг', 'не могу', 'заблокирован', 'взлом', 'мошенник'
        ]

        medium_priority_keywords = [
            'вопрос', 'помощь', 'нужно', 'хочу', 'предложение', 'улучшение'
        ]

        message_lower = message.lower()

        if feedback_type in ['complaint', 'bug_report']:
            if any(keyword in message_lower for keyword in high_priority_keywords):
                return 4  # Высокий
            return 3  # Средний
        elif feedback_type in ['feature_request', 'suggestion']:
            return 2  # Низкий
        else:
            if any(keyword in message_lower for keyword in high_priority_keywords):
                return 3
            elif any(keyword in message_lower for keyword in medium_priority_keywords):
                return 2
            return 1

    def get_feedback_statistics(self) -> Dict:
        """Возвращает статистику по обратной связи"""
        stats = UserFeedback.objects.aggregate(
            total_feedbacks=Count('id'),
            new_feedbacks=Count('id', filter=Q(status='new')),
            in_review_feedbacks=Count('id', filter=Q(status='in_review')),
            in_progress_feedbacks=Count('id', filter=Q(status='in_progress')),
            resolved_feedbacks=Count('id', filter=Q(status='resolved')),
            avg_rating=Avg('rating__rating')
        )

        # Статистика по типам
        type_stats = {}
        for type_choice, type_name in UserFeedback.FEEDBACK_TYPES:
            count = UserFeedback.objects.filter(feedback_type=type_choice).count()
            type_stats[type_name] = count

        # Статистика по категориям
        category_stats = {}
        for category in FeedbackCategory.objects.all():
            count = UserFeedback.objects.filter(category=category).count()
            category_stats[category.name] = {
                'count': count,
                'icon': category.icon,
                'color': category.color
            }

        return {
            'total_feedbacks': stats['total_feedbacks'] or 0,
            'by_status': {
                'new': stats['new_feedbacks'] or 0,
                'in_review': stats['in_review_feedbacks'] or 0,
                'in_progress': stats['in_progress_feedbacks'] or 0,
                'resolved': stats['resolved_feedbacks'] or 0
            },
            'by_type': type_stats,
            'by_category': category_stats,
            'average_rating': round(stats['avg_rating'] or 0, 1),
            'response_rate': self._calculate_response_rate()
        }

    def _calculate_response_rate(self) -> float:
        """Рассчитывает процент ответов на обращения"""
        total = UserFeedback.objects.count()
        if total == 0:
            return 0.0

        responded = UserFeedback.objects.filter(
            admin_response__isnull=False
        ).count()

        return round((responded / total) * 100, 1)

    def get_user_feedback_history(self, user: User, limit: int = 10) -> List[Dict]:
        """Возвращает историю обращений пользователя"""
        feedbacks = UserFeedback.objects.filter(
            user=user
        ).order_by('-created_at')[:limit]

        result = []
        for feedback in feedbacks:
            result.append({
                'id': str(feedback.id),
                'title': feedback.title,
                'type': feedback.get_feedback_type_display(),
                'status': feedback.get_status_display(),
                'status_code': feedback.status,
                'category': feedback.category.name if feedback.category else 'Без категории',
                'priority': feedback.get_priority_display(),
                'message': feedback.message[:100] + '...' if len(feedback.message) > 100 else feedback.message,
                'admin_response': feedback.admin_response[:100] + '...' if len(feedback.admin_response) > 100 else feedback.admin_response,
                'created_at': feedback.created_at.strftime('%d.%m.%Y %H:%M'),
                'responded_at': feedback.responded_at.strftime('%d.%m.%Y %H:%M') if feedback.responded_at else None,
                'response_time_hours': feedback.response_time_hours,
                'rating': feedback.rating.rating if hasattr(feedback, 'rating') else None
            })

        return result

    def rate_feedback_response(self, feedback_id: str, rating: int, comment: str = '') -> Dict:
        """Оценивает полезность ответа на обратную связь"""
        try:
            feedback = UserFeedback.objects.get(id=feedback_id)

            if not feedback.admin_response:
                return {
                    'success': False,
                    'error': 'Нельзя оценить ответ, который еще не был дан'
                }

            if hasattr(feedback, 'rating'):
                # Обновляем существующую оценку
                feedback.rating.rating = rating
                feedback.rating.comment = comment
                feedback.rating.save()
            else:
                # Создаем новую оценку
                FeedbackRating.objects.create(
                    feedback=feedback,
                    rating=rating,
                    comment=comment
                )

            return {
                'success': True,
                'message': 'Спасибо за оценку! Это поможет нам улучшить качество поддержки.'
            }

        except UserFeedback.DoesNotExist:
            return {
                'success': False,
                'error': 'Обращение не найдено'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Произошла ошибка: {str(e)}'
            }

    def get_feedback_for_ai_assistant(self, limit: int = 5) -> List[Dict]:
        """Возвращает подходящие обращения для ответа через ИИ-ассистента"""
        # Берем новые обращения средней и низкой приоритетности
        feedbacks = UserFeedback.objects.filter(
            status='new',
            priority__in=[1, 2]
        ).order_by('created_at')[:limit]

        result = []
        for feedback in feedbacks:
            result.append({
                'id': str(feedback.id),
                'title': feedback.title,
                'message': feedback.message,
                'type': feedback.get_feedback_type_display(),
                'category': feedback.category.name if feedback.category else 'Без категории',
                'user_name': feedback.user.get_full_name() or feedback.user.username if feedback.user else 'Аноним',
                'user_email': feedback.email,
                'created_at': feedback.created_at.strftime('%d.%m.%Y %H:%M')
            })

        return result

    def suggest_quick_responses(self, feedback_type: str, message: str) -> List[str]:
        """Предлагает быстрые ответы для常见 типов обращений"""
        message_lower = message.lower()

        if feedback_type == 'question':
            if 'клуб' in message_lower:
                return [
                    "Спасибо за вопрос о клубах! Наша платформа предлагает различные сообщества по интересам. Вы можете найти подходящий клуб через каталог или создать свой собственный.",
                    "Интересный вопрос! Клубы на нашей платформе объединяют людей по интересам. Какая тема вам интересна?"
                ]
            elif 'создать' in message_lower:
                return [
                    "Создать клуб очень просто! Заполните форму создания клуба, добавьте описание и пригласите участников.",
                    "Отличная идея! Я могу помочь вам с созданием клуба. Расскажите подробнее о вашей концепции."
                ]
            else:
                return [
                    "Спасибо за ваш вопрос! Я постараюсь помочь вам. Расскажите подробнее о том, что вас интересует.",
                    "Интересный вопрос! Давайте разберемся вместе."
                ]

        elif feedback_type == 'suggestion':
            return [
                "Спасибо за ваше предложение! Мы ценим идеи пользователей и рассмотрим ваше предложение.",
                "Отличное предложение! Мы обязательно изучим его в ближайшее время."
            ]

        elif feedback_type == 'complaint':
            return [
                "Приносим извинения за неудобства! Мы разберемся в вашей ситуации как можно скорее.",
                "Нам жаль, что вы столкнулись с проблемой. Помогите нам разобраться в деталях."
            ]

            return [
                "Спасибо за ваше обращение! Мы получили ваше сообщение и ответим в ближайшее время.",
                "Ваше сообщение важно для нас. Мы свяжемся с вами в ближайшее время."
            ]

    def get_guidance(self, message: str) -> str:
        """
        Возвращает руководство по обратной связи
        """
        message_lower = message.lower()

        # Инициализируем категории, если они еще не созданы
        self.initialize_categories()

        if any(word in message_lower for word in ['жалоба', 'проблема', 'ошибка', 'баг', 'не работает']):
            return """🆘 **Сообщить о проблеме или ошибке**

Спасибо, что помогаете нам улучшить платформу!

**📝 Как правильно описать проблему:**
• Что именно не работает?
• Что вы делали перед возникновением проблемы?
• Какой результат вы ожидали?
• Браузер и устройство, которые вы используете

**🔧 Быстрые решения:**
- Перезагрузите страницу (Ctrl+F5)
- Попробуйте другой браузер
- Проверьте интернет-соединение
- Очистите кэш браузера

**📨 Способы сообщить о проблеме:**
1. **Здесь в чате** - опишите проблему подробно
2. **Через форму обратной связи** - если нужно приложить скриншоты
3. **На email:** support@fan-club.kz

**⏡ Среднее время ответа:** 2-4 часа в рабочее время

Расскажите подробнее о вашей проблеме?"""

        elif any(word in message_lower for word in ['предложение', 'идея', 'улучшение', 'фича']):
            return """💡 **Предложить идею или улучшение**

Спасибо за ваши идеи! Они помогают нам делать платформу лучше.

**🎯 Что можно предложить:**
• Новые функции для клубов
• Улучшения интерфейса
• Новые категории мероприятий
• Интеграцию с другими сервисами
• Образовательные программы

**📝 Как описать предложение:**
1. **Проблема:** Какую проблему решает ваша идея?
2. **Решение:** Как именно должно работать?
3. **Ценность:** Почему это будет полезно другим пользователям?
4. **Пример:** Как бы вы этим пользовались?

**🏆 Лучшие предложения получают:**
• Приоритет в разработке
• Бонусы и благодарности
• Mention в релиз-нотах

Расскажите вашу идею!"""

        elif any(word in message_lower for word in ['отзыв', 'мнение', 'оценка']):
            return """⭐ **Оставить отзыв о платформе**

Ваше мнение очень важно для нас!

**📋 Что можно оценить:**
• Удобство использования сайта
• Разнообразие клубов и мероприятий
• Качество общения в сообществах
• Работа ИИ-ассистента 😉
• Скорость поддержки

**💭 Форма отзыва:**
1. **Что понравилось** - конкретные примеры
2. **Что можно улучшить** - конструктивные предложения
3. **Самое полезное** - что помогает вам больше всего
4. **Желаемое будущее** - чего не хватает?

**🎁 За подробные отзывы:**
• Персональные рекомендации
• Доступ к бета-функциям
• Участие в фокус-группах

Хотите поделиться впечатлениями?"""

        else:
            return """📮 **Обратная связь на ЦЕНТР СОБЫТИЙ**

Мы ценим каждое ваше сообщение! Вот как можно с нами связаться:

**🗂️ Категории обращений:**
💬 **Общие вопросы** - о платформе и возможностях
🔧 **Техническая поддержка** - проблемы, ошибки, баги
✨ **Предложения** - новые функции и улучшения
📚 **Контент** - информация о клубах, мероприятиях
🤝 **Сотрудничество** - партнерство и проекты
⚠️ **Жалобы** - нарушения и проблемы

**📝 Как написать хорошее обращение:**
• Четкий заголовок
• Подробное описание
• Конкретные примеры
• Желаемый результат

**⏡ Сроки ответа:**
• Простые вопросы: 1-2 часа
• Технические проблемы: 2-4 часа
• Предложения: 1-2 дня
• Сложные вопросы: до 3 дней

**🎯 Расскажите:**
1. Что вас интересует?
2. Это вопрос, предложение или проблема?
3. Как я могу вам помочь?

Я здесь, чтобы помочь! ✨"""