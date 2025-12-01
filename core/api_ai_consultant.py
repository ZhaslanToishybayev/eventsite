"""
🎯 AI Club Consultant API - REST API для AI консультанта по клубам

Этот модуль предоставляет REST API endpoints для взаимодействия с AI консультантом.
Реализует интеграцию GPT-4o mini с Django ORM и существующими данными о клубах.

Основные функции:
- /api/ai/consult/ - Основной endpoint для AI консультаций
- /api/ai/clubs/search/ - Поиск клубов с AI поддержкой
- /api/ai/clubs/recommend/ - AI рекомендации клубов
- /api/ai/clubs/create/ - Диалоговое создание клубов
"""

import os
import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional

from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.conf import settings
from django.core.cache import cache
import django

# Настройка Django для использования в standalone скриптах
if not settings.configured:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    django.setup()

from clubs.models import Club, ClubCategory, City
from accounts.models import User
from django.db.models import Q

logger = logging.getLogger(__name__)

# Инициализация AI консультанта
try:
    from ai_club_consultant import AIClubConsultant
    ai_consultant = AIClubConsultant()
    AI_AVAILABLE = True
except ImportError as e:
    logger.error(f"Failed to import AI consultant: {e}")
    AI_AVAILABLE = False
    ai_consultant = None


@csrf_exempt
@require_http_methods(["POST"])
def api_ai_consult(request: HttpRequest) -> JsonResponse:
    """
    Основной endpoint для AI консультаций

    POST /api/ai/consult/
    {
        "message": "Найди музыкальные клубы в Алматы",
        "user_id": 123,  # опционально
        "location": "Алматы"  # опционально
    }

    Returns:
    {
        "status": "success",
        "response": {
            "type": "recommendations",
            "content": "Текст ответа AI",
            "clubs": [...],
            "suggestions": [...]
        },
        "timestamp": "2024-11-27T21:45:00Z"
    }
    """
    if not AI_AVAILABLE:
        return JsonResponse({
            'status': 'error',
            'message': 'AI консультант временно недоступен'
        }, status=503)

    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        user_id = data.get('user_id')
        location = data.get('location')

        if not message:
            return JsonResponse({
                'status': 'error',
                'message': 'Пустое сообщение'
            }, status=400)

        # Получение пользователя (если авторизован)
        user = None
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                pass

        # Обработка сообщения через AI консультант
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            response = loop.run_until_complete(
                ai_consultant.process_user_message(
                    message=message,
                    user_id=user_id,
                    location=location
                )
            )
        finally:
            loop.close()

        return JsonResponse({
            'status': 'success',
            'response': response,
            'timestamp': datetime.now().isoformat()
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Некорректный JSON'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in AI consultation: {e}")
        return JsonResponse({
            'status': 'error',
            'message': 'Ошибка обработки запроса'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_ai_clubs_search(request: HttpRequest) -> JsonResponse:
    """
    Поиск клубов с AI поддержкой

    GET /api/ai/clubs/search/?q=музыка&city=Алматы&limit=10

    Returns:
    {
        "status": "success",
        "data": {
            "clubs": [...],
            "total": 25,
            "search_info": {
                "query": "музыка",
                "city": "Алматы",
                "results_count": 10
            }
        }
    }
    """
    try:
        query = request.GET.get('q', '').strip()
        city = request.GET.get('city', '').strip()
        limit = min(int(request.GET.get('limit', 10)), 50)  # Максимум 50

        if not query and not city:
            return JsonResponse({
                'status': 'error',
                'message': 'Требуется параметр поиска (q или city)'
            }, status=400)

        # Поиск клубов
        clubs = Club.objects.filter(is_active=True)

        if query:
            clubs = clubs.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(activities__icontains=query) |
                Q(skills_developed__icontains=query)
            )

        if city:
            clubs = clubs.filter(city__name__icontains=city)

        clubs = clubs.select_related('city', 'category').prefetch_related('members')

        total = clubs.count()
        clubs_list = []

        for club in clubs[:limit]:
            club_data = {
                'id': str(club.id),
                'name': club.name,
                'description': club.description,
                'city': {
                    'id': str(club.city.id) if club.city else None,
                    'name': club.city.name if club.city else None
                } if club.city else None,
                'category': {
                    'id': str(club.category.id) if club.category else None,
                    'name': club.category.name if club.category else None
                } if club.category else None,
                'members_count': club.members_count,
                'activities': club.activities,
                'skills_developed': club.skills_developed,
                'target_audience': club.target_audience,
                'is_active': club.is_active,
                'created_at': club.created_at.isoformat(),
                'logo': club.logo.url if club.logo else None,
                'email': club.email,
                'phone': club.phone,
                'address': club.address,
                'likes_count': getattr(club, 'likes_count', 0),
                'partners_count': getattr(club, 'partners_count', 0)
            }
            clubs_list.append(club_data)

        return JsonResponse({
            'status': 'success',
            'data': {
                'clubs': clubs_list,
                'total': total,
                'search_info': {
                    'query': query,
                    'city': city,
                    'results_count': len(clubs_list),
                    'limit': limit
                }
            },
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error in AI clubs search: {e}")
        return JsonResponse({
            'status': 'error',
            'message': 'Ошибка поиска клубов'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_ai_clubs_recommend(request: HttpRequest) -> JsonResponse:
    """
    AI рекомендации клубов на основе интересов

    POST /api/ai/clubs/recommend/
    {
        "interests": ["музыка", "пение"],
        "location": "Алматы",
        "user_id": 123,
        "preferences": {
            "age_group": "18-35",
            "activity_level": "средний"
        }
    }

    Returns:
    {
        "status": "success",
        "recommendations": [
            {
                "club": {...},
                "relevance_score": 9.5,
                "reasons": ["Подходит по интересам", "В вашем городе"],
                "suggested_questions": [...]
            }
        ],
        "total_found": 25
    }
    """
    if not AI_AVAILABLE:
        return JsonResponse({
            'status': 'error',
            'message': 'AI рекомендации временно недоступны'
        }, status=503)

    try:
        data = json.loads(request.body)
        interests = data.get('interests', [])
        location = data.get('location')
        user_id = data.get('user_id')
        preferences = data.get('preferences', {})

        if not interests and not location:
            return JsonResponse({
                'status': 'error',
                'message': 'Требуются интересы или локация'
            }, status=400)

        # Получение пользователя для персонализации
        user_context = None
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                # Можно добавить логику получения предпочтений пользователя
            except User.DoesNotExist:
                pass

        # Поиск клубов по критериям
        clubs = Club.objects.filter(is_active=True)

        if location:
            clubs = clubs.filter(city__name__icontains=location)

        if interests:
            interests_filter = Q()
            for interest in interests:
                interests_filter |= (
                    Q(description__icontains=interest) |
                    Q(activities__icontains=interest) |
                    Q(skills_developed__icontains=interest) |
                    Q(target_audience__icontains=interest)
                )
            clubs = clubs.filter(interests_filter)

        clubs = clubs.select_related('city', 'category')[:20]
        recommendations = []

        # Расчет релевантности для каждого клуба
        for club in clubs:
            relevance_score = _calculate_club_relevance(club, interests, location, preferences)
            reasons = _generate_match_reasons(club, interests, location, preferences)

            recommendation = {
                'club': {
                    'id': str(club.id),
                    'name': club.name,
                    'description': club.description[:200],
                    'city': club.city.name if club.city else None,
                    'category': club.category.name if club.category else None,
                    'members_count': club.members_count,
                    'logo': club.logo.url if club.logo else None
                },
                'relevance_score': relevance_score,
                'reasons': reasons,
                'suggested_questions': [
                    f"Расскажи подробнее о {club.name}",
                    f"Какие мероприятия проводит {club.name}",
                    f"Для кого подходит {club.name}"
                ]
            }
            recommendations.append(recommendation)

        # Сортировка по релевантности
        recommendations.sort(key=lambda x: x['relevance_score'], reverse=True)

        return JsonResponse({
            'status': 'success',
            'recommendations': recommendations,
            'total_found': len(recommendations),
            'criteria': {
                'interests': interests,
                'location': location,
                'preferences': preferences
            },
            'timestamp': datetime.now().isoformat()
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Некорректный JSON'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in AI clubs recommendation: {e}")
        return JsonResponse({
            'status': 'error',
            'message': 'Ошибка генерации рекомендаций'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_ai_club_create(request: HttpRequest) -> JsonResponse:
    """
    Диалоговое создание клуба через AI

    POST /api/ai/club/create/
    {
        "action": "start",  # start, continue, confirm, cancel
        "user_id": 123,
        "data": {
            "name": "Музыкальный клуб",
            "description": "Занятия музыкой для начинающих",
            "city": "Алматы",
            "category": "Музыка",
            "target_audience": "18-35 лет"
        }
    }

    Returns:
    {
        "status": "success",
        "stage": "name|description|location|category|target_audience|confirmation|completed",
        "content": "Текст от AI",
        "club_data": {...}
    }
    """
    if not AI_AVAILABLE:
        return JsonResponse({
            'status': 'error',
            'message': 'AI создание клубов временно недоступно'
        }, status=503)

    try:
        data = json.loads(request.body)
        action = data.get('action', 'start')
        user_id = data.get('user_id')
        club_data = data.get('data', {})

        if not user_id:
            return JsonResponse({
                'status': 'error',
                'message': 'Требуется авторизация'
            }, status=400)

        # Получение пользователя
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Пользователь не найден'
            }, status=404)

        # Обработка действия
        if action == 'start':
            response = _start_club_creation(user_id)
        elif action == 'continue':
            response = _continue_club_creation(user_id, club_data)
        elif action == 'confirm':
            response = _confirm_club_creation(user_id, club_data, user)
        elif action == 'cancel':
            response = _cancel_club_creation(user_id)
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Некорректное действие'
            }, status=400)

        return JsonResponse({
            'status': 'success',
            'response': response,
            'timestamp': datetime.now().isoformat()
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Некорректный JSON'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in AI club creation: {e}")
        return JsonResponse({
            'status': 'error',
            'message': 'Ошибка создания клуба'
        }, status=500)


# Вспомогательные функции

def _calculate_club_relevance(club: Club, interests: list, location: str, preferences: dict) -> float:
    """Расчет балла релевантности клуба"""
    score = 0.0

    # Базовый балл за активность
    if club.is_active:
        score += 1.0

    # Баллы за соответствие локации
    if location and club.city:
        if location.lower() in club.city.name.lower():
            score += 2.0

    # Баллы за соответствие интересам
    if interests:
        club_text = f"{club.description} {club.activities} {club.skills_developed}".lower()
        for interest in interests:
            if interest.lower() in club_text:
                score += 1.5

    # Баллы за популярность
    if club.members_count > 50:
        score += 2.0
    elif club.members_count > 10:
        score += 1.0

    # Баллы за полноту профиля
    completeness_score = 0
    if club.description:
        completeness_score += 1
    if club.activities:
        completeness_score += 0.5
    if club.skills_developed:
        completeness_score += 0.5
    if club.logo:
        completeness_score += 0.5

    score += (completeness_score / 2.5)  # Нормализация до 1 балла

    return round(score, 1)


def _generate_match_reasons(club: Club, interests: list, location: str, preferences: dict) -> list:
    """Генерация причин соответствия"""
    reasons = []

    if location and club.city and location.lower() in club.city.name.lower():
        reasons.append(f"📍 В вашем городе ({club.city.name})")

    if interests:
        club_text = f"{club.description} {club.activities}".lower()
        matching_interests = [interest for interest in interests if interest.lower() in club_text]
        if matching_interests:
            reasons.append(f"🎯 По интересам: {', '.join(matching_interests[:2])}")

    if club.members_count > 20:
        reasons.append(f"👥 Популярный клуб ({club.members_count} участников)")
    elif club.members_count > 5:
        reasons.append(f"🤝 Активное сообщество ({club.members_count} участников)")

    if club.category:
        reasons.append(f"🏷️ {club.category.name}")

    return reasons[:3]  # Максимум 3 причины


def _start_club_creation(user_id: int) -> dict:
    """Начало процесса создания клуба"""
    # Очистка предыдущих данных
    cache_key = f"club_creation_{user_id}"
    cache.delete(cache_key)

    return {
        'stage': 'name',
        'content': "🎉 Отлично! Давайте создадим новый клуб!\n\n"
                  "1. Какое название вы хотите дать вашему клубу?",
        'input_placeholder': 'Введите название клуба',
        'suggestions': [
            'Музыкальный клуб',
            'Спортивная секция',
            'IT-сообщество',
            'Книжный клуб'
        ]
    }


def _continue_club_creation(user_id: int, club_data: dict) -> dict:
    """Продолжение процесса создания клуба"""
    cache_key = f"club_creation_{user_id}"
    existing_data = cache.get(cache_key, {})

    # Обновление данных
    existing_data.update(club_data)
    cache.set(cache_key, existing_data, timeout=3600)  # 1 час

    # Определение следующего этапа
    if not existing_data.get('name'):
        return {
            'stage': 'name',
            'content': "1. Какое название вы хотите дать вашему клубу?",
            'input_placeholder': 'Введите название клуба'
        }
    elif not existing_data.get('description'):
        return {
            'stage': 'description',
            'content': "2. Чем будет заниматься ваш клуб? Опишите основную деятельность.",
            'input_placeholder': 'Описание деятельности клуба',
            'suggestions': [
                'Занятия музыкой и пением',
                'Спортивные тренировки',
                'IT-встречи и хакатоны',
                'Чтение и обсуждение книг'
            ]
        }
    elif not existing_data.get('city'):
        return {
            'stage': 'city',
            'content': "3. Где будет находиться клуб?",
            'input_placeholder': 'Город или район',
            'suggestions': ['Алматы', 'Астана', 'Шымкент', 'Онлайн']
        }
    elif not existing_data.get('category'):
        categories = list(ClubCategory.objects.all().values_list('name', flat=True))
        return {
            'stage': 'category',
            'content': "4. К какой категории относится ваш клуб?",
            'input_placeholder': 'Выберите категорию',
            'suggestions': categories[:5]  # Первые 5 категорий
        }
    elif not existing_data.get('target_audience'):
        return {
            'stage': 'target_audience',
            'content': "5. Для кого предназначен клуб? (возраст, интересы, уровень подготовки)",
            'input_placeholder': 'Целевая аудитория',
            'suggestions': [
                'Для взрослых (18-45)',
                'Для студентов',
                'Для детей и подростков',
                'Для профессионалов'
            ]
        }
    else:
        return {
            'stage': 'confirmation',
            'content': "✅ Проверьте информацию о вашем клубе:\n\n"
                      f"• **Название**: {existing_data['name']}\n"
                      f"• **Описание**: {existing_data['description']}\n"
                      f"• **Город**: {existing_data['city']}\n"
                      f"• **Категория**: {existing_data['category']}\n"
                      f"• **Целевая аудитория**: {existing_data['target_audience']}\n\n"
                      "Все верно?"
        }


def _confirm_club_creation(user_id: int, club_data: dict, user: User) -> dict:
    """Подтверждение и создание клуба"""
    try:
        # Создание клуба в базе данных
        city_name = club_data.get('city', '')
        category_name = club_data.get('category', '')

        # Получение или создание города
        city, _ = City.objects.get_or_create(
            name=city_name,
            defaults={'iata_code': city_name[:3].upper()}
        )

        # Получение или создание категории
        category, _ = ClubCategory.objects.get_or_create(
            name=category_name,
            defaults={'is_active': True}
        )

        # Создание клуба
        club = Club.objects.create(
            name=club_data['name'],
            description=club_data['description'],
            city=city,
            category=category,
            target_audience=club_data.get('target_audience', ''),
            activities=club_data.get('description', ''),
            is_active=True,
            is_private=False,
            members_count=1,  # Создатель становится первым участником
            creater=user
        )

        # Очистка данных создания
        cache_key = f"club_creation_{user_id}"
        cache.delete(cache_key)

        return {
            'stage': 'completed',
            'content': f"🎉 Отлично! Клуб **{club.name}** успешно создан!\n\n"
                      f"Теперь вы можете:\n"
                      f"• Приглашать друзей в клуб\n"
                      f"• Создавать мероприятия\n"
                      f"• Добавлять фотографии\n"
                      f"• Настраивать настройки клуба\n\n"
                      f"Клуб доступен по ссылке: /clubs/{club.id}",
            'club_id': str(club.id),
            'club_name': club.name
        }

    except Exception as e:
        logger.error(f"Error creating club: {e}")
        return {
            'stage': 'error',
            'content': f"❌ Произошла ошибка при создании клуба: {str(e)}\n\n"
                      "Пожалуйста, попробуйте еще раз или обратитесь в поддержку."
        }


def _cancel_club_creation(user_id: int) -> dict:
    """Отмена создания клуба"""
    cache_key = f"club_creation_{user_id}"
    cache.delete(cache_key)

    return {
        'stage': 'cancelled',
        'content': "👋 Создание клуба отменено.\n\n"
                  "Если захотите создать клуб позже - просто скажите!"
    }


# Health check endpoint
@require_http_methods(["GET"])
def api_ai_health(request: HttpRequest) -> JsonResponse:
    """
    Проверка работоспособности AI системы

    GET /api/ai/health/

    Returns:
    {
        "status": "success",
        "ai_available": true,
        "models": ["gpt-4o-mini"],
        "features": ["consultation", "recommendation", "club_creation"],
        "database_status": "connected"
    }
    """
    try:
        # Проверка соединения с базой данных
        db_status = Club.objects.count() > 0

        return JsonResponse({
            'status': 'success',
            'ai_available': AI_AVAILABLE,
            'models': ['gpt-4o-mini'] if AI_AVAILABLE else [],
            'features': [
                'consultation',
                'recommendation',
                'club_search',
                'club_creation'
            ] if AI_AVAILABLE else [],
            'database_status': 'connected' if db_status else 'disconnected',
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JsonResponse({
            'status': 'error',
            'message': 'Health check failed',
            'database_status': 'error'
        }, status=500)