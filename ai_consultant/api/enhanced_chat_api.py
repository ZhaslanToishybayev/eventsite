"""
🤖 Enhanced AI Chat API
Улучшенный API для AI чата с реальной интеграцией базы данных
"""

import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.utils import timezone
from django.db.models import Q, Count

from clubs.models import Club, ClubCategory, City
from ai_consultant.services.enhanced_ai_service import EnhancedAIConsultantService

logger = logging.getLogger('ai_consultant')

# Глобальный экземпляр сервиса для эффективности
ai_service = EnhancedAIConsultantService()

@csrf_exempt
@require_http_methods(["POST"])
def enhanced_ai_chat(request):
    """
    Улучшенный AI чат с реальной интеграцией базы данных

    Request:
    {
        "message": "Текст сообщения пользователя",
        "session_id": "Идентификатор сессии",
        "user_id": "ID пользователя (опционально)"
    }

    Response:
    {
        "status": "success",
        "response": "AI ответ",
        "intent": "Тип запроса",
        "metadata": {
            "clubs_found": 5,
            "categories_available": 12,
            "cities_available": 8
        },
        "timestamp": "2025-11-28T15:30:45.907954"
    }
    """
    try:
        # Парсим JSON тело запроса
        data = json.loads(request.body.decode('utf-8'))
        message = data.get('message', '').strip()
        session_id = data.get('session_id', 'default_session')
        user_id = data.get('user_id')

        if not message:
            return JsonResponse({
                'status': 'error',
                'error': 'Пустое сообщение',
                'details': 'Текст сообщения не может быть пустым'
            }, status=400)

        # Обрабатываем сообщение через улучшенный AI сервис
        result = ai_service.process_user_message(message)

        # Собираем метаданные для ответа
        metadata = {
            'clubs_available': Club.objects.filter(is_active=True).count(),
            'categories_available': ClubCategory.objects.filter(is_active=True).count(),
            'cities_available': City.objects.count(),
            'session_id': session_id
        }

        # Если был поиск клубов, добавляем информацию о найденных
        if result.get('intent') in ['club_search', 'club_info'] and result.get('parameters'):
            metadata['search_params'] = result['parameters']

        response_data = {
            'status': 'success',
            'response': result['response'],
            'intent': result['intent'],
            'metadata': metadata,
            'timestamp': timezone.now().isoformat()
        }

        logger.info(f"Enhanced AI chat request processed: session={session_id}, intent={result['intent']}")

        return JsonResponse(response_data)

    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'error': 'Некорректный JSON',
            'details': 'Тело запроса должно быть валидным JSON'
        }, status=400)

    except Exception as e:
        logger.error(f"Error in enhanced AI chat: {str(e)}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'error': 'Внутренняя ошибка сервера',
            'details': 'Произошла ошибка при обработке запроса'
        }, status=500)

@require_http_methods(["GET"])
def enhanced_ai_health(request):
    """
    Health check для улучшенного AI сервиса

    Response:
    {
        "status": "healthy",
        "service": "enhanced_ai_chat",
        "database": {
            "clubs": 156,
            "categories": 12,
            "cities": 8
        },
        "features": [
            "club_search",
            "club_recommendations",
            "club_info",
            "club_creation_guidance"
        ]
    }
    """
    try:
        db_stats = {
            'clubs': Club.objects.filter(is_active=True).count(),
            'categories': ClubCategory.objects.filter(is_active=True).count(),
            'cities': City.objects.count()
        }

        return JsonResponse({
            'status': 'healthy',
            'service': 'enhanced_ai_chat',
            'database': db_stats,
            'features': [
                'club_search',
                'club_recommendations',
                'club_info',
                'club_creation_guidance'
            ],
            'timestamp': timezone.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e)
        }, status=500)

@require_http_methods(["GET"])
def club_search_api(request):
    """
    API для поиска клубов (для интеграции с фронтендом)

    Query parameters:
    - q: Поисковый запрос
    - city: Город
    - category: Категория
    - limit: Лимит результатов (макс 20)

    Response:
    {
        "clubs": [
            {
                "id": "uuid",
                "name": "Название клуба",
                "category": "Категория",
                "city": "Город",
                "members_count": 150,
                "description": "Описание...",
                "is_featured": true
            }
        ],
        "total": 5
    }
    """
    try:
        query = request.GET.get('q', '')
        city_filter = request.GET.get('city', '')
        category_filter = request.GET.get('category', '')
        limit = min(int(request.GET.get('limit', 10)), 20)

        # Формируем параметры поиска
        search_params = {}
        if city_filter:
            search_params['city'] = city_filter
        if category_filter:
            search_params['category'] = category_filter
        if query:
            search_params['interests'] = [query]

        # Используем AI сервис для поиска
        clubs = ai_service.search_clubs(search_params, limit)

        # Форматируем результат
        clubs_data = []
        for club in clubs:
            club_data = {
                'id': str(club.id),
                'name': club.name,
                'category': club.category.name,
                'city': club.city.name if club.city else 'Не указан',
                'members_count': club.members_count,
                'likes_count': club.likes_count,
                'description': club.description[:200] + '...' if len(club.description) > 200 else club.description,
                'is_featured': club.is_featured,
                'address': club.address if club.address != 'No location' else '',
                'email': club.email,
                'phone': club.phone
            }
            clubs_data.append(club_data)

        return JsonResponse({
            'clubs': clubs_data,
            'total': len(clubs_data)
        })

    except Exception as e:
        logger.error(f"Error in club search API: {str(e)}")
        return JsonResponse({
            'error': 'Ошибка при поиске клубов',
            'details': str(e)
        }, status=500)

@require_http_methods(["GET"])
def club_categories_api(request):
    """
    API для получения списка категорий

    Response:
    {
        "categories": [
            {"id": "uuid", "name": "Спорт", "count": 25},
            {"id": "uuid", "name": "Образование", "count": 18}
        ]
    }
    """
    try:
        categories = ClubCategory.objects.filter(is_active=True).annotate(
            club_count=Count('clubs', filter=Q(clubs__is_active=True))
        ).values('id', 'name', 'club_count')

        return JsonResponse({
            'categories': list(categories)
        })

    except Exception as e:
        logger.error(f"Error in categories API: {str(e)}")
        return JsonResponse({
            'error': 'Ошибка при получении категорий',
            'details': str(e)
        }, status=500)

@require_http_methods(["GET"])
def cities_api(request):
    """
    API для получения списка городов

    Response:
    {
        "cities": [
            {"id": "uuid", "name": "Алматы", "count": 45},
            {"id": "uuid", "name": "Нур-Султан", "count": 32}
        ]
    }
    """
    try:
        cities = City.objects.annotate(
            club_count=Count('clubs', filter=Q(clubs__is_active=True))
        ).values('id', 'name', 'club_count').order_by('name')

        return JsonResponse({
            'cities': list(cities)
        })

    except Exception as e:
        logger.error(f"Error in cities API: {str(e)}")
        return JsonResponse({
            'error': 'Ошибка при получении городов',
            'details': str(e)
        }, status=500)