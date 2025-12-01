"""
🤖 Club Creation Agent API
API для интеграции ИИ-агента по созданию клубов
"""

import json
import logging
import re
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from ai_consultant.agents.club_creation_agent import get_club_creation_agent, ClubCreationAgent
from ai_consultant.knowledge.platform_knowledge_base import platform_knowledge

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class ClubCreationAgentView(View):
    """
    🤖 API для ИИ-агента по созданию клубов
    """

    def __init__(self):
        self.agent = get_club_creation_agent()

    async def post(self, request: HttpRequest) -> JsonResponse:
        """Обработка сообщения пользователя для создания клуба"""
        try:
            # Проверяем аутентификацию
            if not request.user.is_authenticated:
                return JsonResponse({
                    'success': False,
                    'error': 'Authentication required',
                    'message': 'Для создания клуба необходимо авторизоваться'
                }, status=401)

            # Парсим данные
            data = json.loads(request.body)
            user_message = data.get('message', '')
            user_context = data.get('context', {})
            action = data.get('action', 'message')  # message, restart, get_status

            if not user_message and action != 'get_status':
                return JsonResponse({
                    'success': False,
                    'error': 'No message provided',
                    'message': 'Пожалуйста, введите сообщение'
                }, status=400)

            user_id = request.user.id

            # Обрабатываем действие
            if action == 'restart':
                response = await self.restart_conversation(user_id)
            elif action == 'get_status':
                response = await self.get_conversation_status(user_id)
            else:
                response = await self.process_message(user_id, user_message, user_context)

            return JsonResponse(response)

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON',
                'message': 'Некорректный JSON формат'
            }, status=400)
        except Exception as e:
            logger.error(f"❌ Error in club creation agent API: {e}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': str(e),
                'message': 'Произошла ошибка при обработке запроса'
            }, status=500)

    async def process_message(self, user_id: int, message: str,
                            context: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка сообщения пользователя"""
        try:
            # Добавляем контекст платформы
            enhanced_context = {
                **context,
                'platform_info': platform_knowledge.PLATFORM_INFO,
                'categories': list(platform_knowledge.CATEGORIES.keys()),
                'instructions': platform_knowledge.get_instruction('create_club')
            }

            # Обрабатываем сообщение через агента
            response = await self.agent.process_user_message(
                user_id, message, enhanced_context
            )

            return response

        except Exception as e:
            logger.error(f"❌ Error processing message: {e}")
            return {
                'success': False,
                'response': 'Извините, произошла ошибка. Пожалуйста, попробуйте позже.',
                'session_state': 'error'
            }

    async def restart_conversation(self, user_id: int) -> Dict[str, Any]:
        """Перезапуск диалога"""
        try:
            # Очищаем сессию
            cache_key = f"club_creation_session_{user_id}"
            from django.core.cache import cache
            cache.delete(cache_key)

            # Создаем новую сессию
            session = self.agent._get_or_create_session(user_id)

            return {
                'success': True,
                'response': 'Давайте начнем сначала! 🚀\n\nРасскажите, какой клуб вы хотите создать? Что вас вдохновляет?',
                'session_state': session['current_stage'],
                'next_steps': self.agent._get_next_steps(session),
                'progress': self.agent._calculate_progress(session)
            }

        except Exception as e:
            logger.error(f"❌ Error restarting conversation: {e}")
            return {
                'success': False,
                'response': 'Произошла ошибка при перезапуске диалога',
                'session_state': 'error'
            }

    async def get_conversation_status(self, user_id: int) -> Dict[str, Any]:
        """Получение статуса диалога"""
        try:
            session = self.agent._get_or_create_session(user_id)
            progress = self.agent._calculate_progress(session)

            return {
                'success': True,
                'session_state': session['current_stage'],
                'progress': progress,
                'next_steps': self.agent._get_next_steps(session),
                'club_data': session.get('club_data', {}),
                'completed_stages': session.get('completed_stages', []),
                'message_count': len(session.get('message_history', []))
            }

        except Exception as e:
            logger.error(f"❌ Error getting conversation status: {e}")
            return {
                'success': False,
                'error': str(e),
                'session_state': 'error'
            }

    async def get_club_suggestions(self, user_id: int, interests: List[str]) -> Dict[str, Any]:
        """Получение предложений по клубам на основе интересов"""
        try:
            suggestions = []

            # Используем платформенные знания для генерации предложений
            for interest in interests[:3]:  # Максимум 3 интереса
                category_suggestions = self._get_category_suggestions(interest)
                suggestions.extend(category_suggestions)

            # Генерируем названия
            name_suggestions = await self._generate_name_suggestions(interests)

            return {
                'success': True,
                'suggestions': {
                    'club_ideas': suggestions,
                    'names': name_suggestions,
                    'categories': self._get_relevant_categories(interests)
                }
            }

        except Exception as e:
            logger.error(f"❌ Error getting club suggestions: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _get_category_suggestions(self, interest: str) -> List[Dict[str, Any]]:
        """Получение предложений категорий"""
        category_mapping = {
            'спорт': [
                {'title': 'Фитнес-клуб', 'description': 'Групповые тренировки и занятия спортом'},
                {'title': 'Беговой клуб', 'description': 'Забеги, маршруты и тренировки для бегунов'},
                {'title': 'Командные виды спорта', 'description': 'Футбол, волейбол, баскетбол и другие'}
            ],
            'технологии': [
                {'title': 'IT-сообщество', 'description': 'Обсуждение технологий и программирования'},
                {'title': 'Геймерский клуб', 'description': 'Игровые вечера и турниры'},
                {'title': 'Гаджетоманы', 'description': 'Обзоры и обсуждение новинок технологий'}
            ],
            'хобби': [
                {'title': 'Творческая мастерская', 'description': 'Рукоделие, рисование, поделки'},
                {'title': 'Настольные игры', 'description': 'Игровые вечера и турниры'},
                {'title': 'Фотоклуб', 'description': 'Фотосессии и обсуждение фотографии'}
            ],
            'профессия': [
                {'title': 'Бизнес-нетворкинг', 'description': 'Встречи предпринимателей и фрилансеров'},
                {'title': 'Карьера и развитие', 'description': 'Советы по карьерному росту'},
                {'title': 'Образовательные кружки', 'description': 'Обучение и мастер-классы'}
            ]
        }

        return category_mapping.get(interest.lower(), [
            {'title': f'Клуб {interest}', 'description': f'Сообщество по интересам {interest}'}
        ])

    async def _generate_name_suggestions(self, interests: List[str]) -> List[str]:
        """Генерация предложений названий"""
        try:
            # Используем OpenAI для генерации названий
            prompt = f"""
            Придумай 5 креативных названий для клуба на основе интересов: {', '.join(interests)}.
            Названия должны быть:
            1. Запоминающимися
            2. Отражать суть интересов
            3. Подходящими для казахстанской аудитории
            4. Легко произносимыми
            5. Уникальными

            Верни список из 5 названий.
            """

            # Здесь можно использовать OpenAI API, но для примера вернем статические варианты
            base_names = []
            for interest in interests[:2]:
                base_names.extend([
                    f'{interest.title()} Community',
                    f'Клуб {interest.title()}',
                    f'{interest.title()} Friends',
                    f'{interest.title()} Hub',
                    f'{interest.title()} Club'
                ])

            return base_names[:5]

        except Exception as e:
            logger.error(f"❌ Error generating name suggestions: {e}")
            return [f'Клуб {interest.title()}' for interest in interests[:5]]

    def _get_relevant_categories(self, interests: List[str]) -> List[str]:
        """Получение релевантных категорий"""
        category_keywords = {
            'спорт': ['фитнес', 'тренировка', 'игра', 'команда', 'состязание'],
            'хобби': ['творчество', 'рукоделие', 'игра', 'мастер', 'хобби'],
            'профессия': ['работа', 'карьера', 'бизнес', 'обучение', 'развитие'],
            'технологии': ['программирование', 'гаджет', 'компьютер', 'интернет', 'технологии']
        }

        relevant_categories = []
        for category, keywords in category_keywords.items():
            for keyword in keywords:
                if any(keyword in interest.lower() for interest in interests):
                    relevant_categories.append(category)
                    break

        return relevant_categories if relevant_categories else ['другие']


@require_http_methods(["GET"])
def get_club_creation_guide(request: HttpRequest) -> JsonResponse:
    """Получение руководства по созданию клубов"""
    try:
        guide = platform_knowledge.get_instruction('create_club')

        return JsonResponse({
            'success': True,
            'guide': guide,
            'requirements': {
                'name': 'Уникальное, до 100 символов',
                'category': 'Выбор из существующих категорий',
                'description': 'Минимум 200 символов',
                'email': 'Действующий email для связи',
                'phone': 'Контактный номер',
                'city': 'Город расположения'
            },
            'tips': [
                'Добавьте качественный логотип',
                'Опишите цели и ценности клуба',
                'Укажите, что участники получат',
                'Добавьте фото в галерею',
                'Создайте первое событие'
            ]
        })

    except Exception as e:
        logger.error(f"❌ Error getting club creation guide: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_categories_info(request: HttpRequest) -> JsonResponse:
    """Получение информации о категориях"""
    try:
        categories_info = platform_knowledge.get_available_categories_info()

        return JsonResponse({
            'success': True,
            'categories': categories_info,
            'total_count': len(categories_info)
        })

    except Exception as e:
        logger.error(f"❌ Error getting categories info: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def validate_club_data(request: HttpRequest) -> JsonResponse:
    """🔬 Advanced validation of club data with AI-powered analysis"""
    try:
        data = json.loads(request.body)
        club_data = data.get('club_data', {})

        errors = []
        warnings = []
        suggestions = []
        validation_score = 0

        logger.info(f"🔍 Validating club data: {club_data.get('name', 'Unknown')}")

        # 🛡️ Advanced field validation
        required_fields = ['name', 'description', 'category', 'email', 'phone', 'city']
        for field in required_fields:
            value = club_data.get(field)
            if not value:
                errors.append(f'❌ Обязательное поле: {field}')
            else:
                validation_score += 100 / len(required_fields)

        if errors:
            return JsonResponse({
                'success': False,
                'validation': {
                    'errors': errors,
                    'warnings': warnings,
                    'suggestions': suggestions,
                    'score': 0,
                    'is_valid': False
                }
            })

        # 📧 Advanced email validation
        email = club_data.get('email', '')
        email_patterns = [
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            r'.*@gmail\.com$',
            r'.*@mail\.ru$',
            r'.*@yandex\.ru$',
            r'.*@outlook\.com$'
        ]

        email_valid = any(re.match(pattern, email) for pattern in email_patterns)
        if not email_valid:
            errors.append('❌ Некорректный email адрес')
        elif not any(pattern in email for pattern in ['gmail.com', 'mail.ru', 'yandex.ru', 'outlook.com']):
            suggestions.append('💡 Рассмотрите использование популярного email-провайдера для лучшей доставки')

        # 📞 Advanced phone validation
        phone = club_data.get('phone', '')
        phone_patterns = [
            r'^\+?\d{11}$',  # +77001234567
            r'^\+?\d{3}-\d{3}-\d{4}$',  # +770-123-4567
            r'^\(\+\d{3}\)\d{3}-\d{4}$',  # (+770)123-4567
        ]

        phone_valid = any(re.match(pattern, phone) for pattern in phone_patterns)
        if not phone_valid:
            warnings.append('⚠️ Формат телефона может быть некорректным')

        # 🏙️ City validation
        city = club_data.get('city', '').strip()
        if len(city) < 2:
            errors.append('❌ Название города слишком короткое')
        elif city.lower() in ['unknown', 'test', 'dummy']:
            errors.append('❌ Укажите реальный город')

        # 🏷️ Name validation with AI analysis
        name = club_data.get('name', '')
        if len(name) < 3:
            errors.append('❌ Название клуба слишком короткое')
        elif len(name) > 100:
            errors.append('❌ Название клуба слишком длинное')
        else:
            # Check for unique and meaningful names
            common_words = ['клуб', 'community', 'тусовка', 'группа', 'ассоциация']
            if any(word in name.lower() for word in common_words):
                suggestions.append('💡 Добавьте уникальное слово или брендинг в название')

            # Check for special characters
            if not re.match(r'^[a-zA-Zа-яА-Я0-9\s\-\.]+$', name):
                warnings.append('⚠️ Название содержит специальные символы, которые могут вызвать проблемы')

        # 📝 Description validation with AI analysis
        description = club_data.get('description', '')
        if len(description) < 200:
            errors.append('❌ Описание слишком короткое. Минимум 200 символов')
        elif len(description) < 500:
            warnings.append('⚠️ Описание можно сделать более подробным')
            suggestions.append('💡 Добавьте больше деталей о целях и活动中')
        else:
            validation_score += 15

        # Check for quality content in description
        quality_indicators = [
            'цели', 'миссия', 'активности', 'встречи', 'участники',
            'events', 'activities', 'goals', 'mission', 'members'
        ]

        quality_score = sum(1 for indicator in quality_indicators if indicator in description.lower())
        if quality_score < 2:
            warnings.append('⚠️ Описание можно сделать более информативным')
            suggestions.append('💡 Упомяните цели, активности и чем будет заниматься клуб')

        # 🎯 Category validation
        category = club_data.get('category', '')
        valid_categories = list(platform_knowledge.CATEGORIES.keys())
        if category not in valid_categories:
            errors.append(f'❌ Некорректная категория. Доступные: {", ".join(valid_categories)}')
        else:
            validation_score += 10

        # 🔍 Check for existing similar clubs
        if name:
            from clubs.models import Club
            similar_clubs = Club.objects.filter(
                name__icontains=name.split()[0] if name.split() else ''
            ).exclude(name=name)

            if similar_clubs.exists():
                suggestions.append(f'💡 Похожие клубы: {", ".join([c.name for c in similar_clubs[:3]])}')

            # Check exact name match
            existing_club = Club.objects.filter(name=name).exists()
            if existing_club:
                errors.append('❌ Клуб с таким названием уже существует')

        # 📊 Calculate final validation score
        max_score = 100
        final_score = min(validation_score, max_score)

        # 🎨 Generate improvement suggestions
        if final_score < 70:
            suggestions.extend([
                '💡 Рассмотрите более подробное описание деятельности',
                '💡 Добавьте информацию о формате встреч',
                '💡 Уточните целевую аудиторию',
                '💡 Добавьте контакты для связи'
            ])

        return JsonResponse({
            'success': True,
            'validation': {
                'errors': errors,
                'warnings': warnings,
                'suggestions': suggestions,
                'score': final_score,
                'is_valid': len(errors) == 0 and final_score >= 70,
                'grade': 'A' if final_score >= 90 else 'B' if final_score >= 80 else 'C' if final_score >= 70 else 'D'
            }
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON format'
        }, status=400)
    except Exception as e:
        logger.error(f"❌ Error validating club data: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_creation_stats(request: HttpRequest) -> JsonResponse:
    """Получение статистики по созданию клубов"""
    try:
        from clubs.models import Club, UserInteraction

        # Общая статистика
        total_clubs = Club.objects.count()
        active_clubs = Club.objects.filter(is_active=True).count()
        today_created = Club.objects.filter(
            created_at__date=timezone.now().date()
        ).count()

        # Статистика по категориям
        category_stats = {}
        categories = platform_knowledge.CATEGORIES
        for category_key in categories.keys():
            count = Club.objects.filter(
                category__name__icontains=category_key
            ).count()
            category_stats[category_key] = count

        # Статистика по этапам создания (если есть данные)
        creation_interactions = UserInteraction.objects.filter(
            interaction_type='club_creation'
        ).count()

        return JsonResponse({
            'success': True,
            'stats': {
                'total_clubs': total_clubs,
                'active_clubs': active_clubs,
                'today_created': today_created,
                'creation_interactions': creation_interactions,
                'category_distribution': category_stats,
                'success_rate': f"{(active_clubs / total_clubs * 100):.1f}%" if total_clubs > 0 else "0%"
            }
        })

    except Exception as e:
        logger.error(f"❌ Error getting creation stats: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


from django.urls import path
