"""
🎯 AI Integration API Views - API для интеграции AI системы с базой данных

Этот файл содержит API endpoints для:
1. Поиска и рекомендации клубов
2. Информации о пользователях
3. AI чата с RAG системой
"""

import json
import logging
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.conf import settings
from clubs.models import Club, ClubCategory, City
from accounts.models import User
from django.db.models import Q
import uuid

# Настройка логирования
logger = logging.getLogger(__name__)

@require_http_methods(["GET"])
def api_clubs(request):
    """Получение списка клубов с фильтрацией"""
    try:
        # Фильтрация по параметрам
        clubs = Club.objects.filter(is_active=True)

        # Фильтрация по городу
        city = request.GET.get('city')
        if city:
            clubs = clubs.filter(city__name__icontains=city)

        # Фильтрация по категории
        category = request.GET.get('category')
        if category:
            clubs = clubs.filter(category__name__icontains=category)

        # Поиск по названию и описанию
        search = request.GET.get('search')
        if search:
            clubs = clubs.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(activities__icontains=search)
            )

        # Подготовка данных
        clubs_data = []
        for club in clubs[:20]:  # Ограничение 20 клубов
            clubs_data.append({
                'id': str(club.id),
                'name': club.name,
                'description': club.description[:300] + '...' if len(club.description) > 300 else club.description,
                'city': club.city.name if club.city else 'Не указан',
                'category': club.category.name if club.category else 'Не указана',
                'members_count': club.members_count,
                'activities': club.activities,
                'skills_developed': club.skills_developed,
                'target_audience': club.target_audience,
                'is_active': club.is_active,
                'created_at': club.created_at.strftime('%Y-%m-%d'),
                'logo': club.logo.url if club.logo else None
            })

        return JsonResponse({
            'status': 'success',
            'data': clubs_data,
            'meta': {
                'total': clubs.count(),
                'returned': len(clubs_data)
            }
        })

    except Exception as e:
        logger.error(f"Error in api_clubs GET: {e}")
        return JsonResponse({
            'status': 'error',
            'message': 'Ошибка при получении клубов'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def api_club_recommendation(request):
    """Получение рекомендаций по запросу пользователя"""
    try:
        data = json.loads(request.body)
        user_query = data.get('query', '').lower()
        location = data.get('location')
        interests = data.get('interests', [])

        # Поиск релевантных клубов
        clubs = Club.objects.filter(is_active=True)

        # Фильтрация по местоположению
        if location:
            clubs = clubs.filter(city__name__icontains=location)

        # Поиск по интересам и ключевым словам
        if user_query:
            clubs = clubs.filter(
                Q(name__icontains=user_query) |
                Q(description__icontains=user_query) |
                Q(activities__icontains=user_query) |
                Q(skills_developed__icontains=user_query) |
                Q(target_audience__icontains=user_query) |
                Q(tags__icontains=user_query)
            )

        # Сортировка по релевантности (пока простая)
        recommended_clubs = []
        for club in clubs[:10]:  # Топ-10 рекомендаций
            # Расчет простого рейтинга релевантности
            relevance_score = 0
            if user_query in club.name.lower():
                relevance_score += 10
            if user_query in club.description.lower():
                relevance_score += 5
            if user_query in club.activities.lower():
                relevance_score += 3

            recommended_clubs.append({
                'id': str(club.id),
                'name': club.name,
                'description': club.description[:200] + '...' if len(club.description) > 200 else club.description,
                'city': club.city.name if club.city else 'Не указан',
                'category': club.category.name if club.category else 'Не указана',
                'members_count': club.members_count,
                'relevance_score': relevance_score,
                'activities': club.activities,
                'skills_developed': club.skills_developed[:100] + '...' if len(club.skills_developed) > 100 else club.skills_developed
            })

        # Сортировка по рейтингу релевантности
        recommended_clubs.sort(key=lambda x: x['relevance_score'], reverse=True)

        return JsonResponse({
            'status': 'success',
            'data': recommended_clubs,
            'query': user_query,
            'location': location
        })

    except Exception as e:
        logger.error(f"Error in api_club_recommendation POST: {e}")
        return JsonResponse({
            'status': 'error',
            'message': 'Ошибка при получении рекомендаций'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def api_ai_chat(request):
    """API для AI чата с RAG системой"""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        user_id = request.user.id if request.user.is_authenticated else None

        if not user_message:
            return JsonResponse({
                'status': 'error',
                'message': 'Пустое сообщение'
            }, status=400)

        # Поиск релевантных клубов для контекста
        relevant_clubs = find_relevant_clubs(user_message)

        # Формирование AI ответа
        ai_response = generate_ai_response(user_message, relevant_clubs, user_id)

        return JsonResponse({
            'status': 'success',
            'response': ai_response,
            'timestamp': datetime.now().isoformat(),
            'relevant_clubs': relevant_clubs[:3]  # Топ-3 релевантных клуба
        })

    except Exception as e:
        logger.error(f"Error in api_ai_chat POST: {e}")
        return JsonResponse({
            'status': 'error',
            'message': 'Ошибка обработки AI запроса'
        }, status=500)

def find_relevant_clubs(user_message):
    """Поиск релевантных клубов на основе сообщения пользователя"""
    clubs = Club.objects.filter(is_active=True)
    user_message_lower = user_message.lower()

    # Поиск по ключевым словам
    relevant_clubs = []
    for club in clubs:
        relevance_score = 0

        # Проверка названия
        if any(word in club.name.lower() for word in ['музыка', 'танцы', 'спорт', 'игры', 'кино', 'книги']):
            if any(word in user_message_lower for word in ['музыка', 'танцы', 'спорт', 'игры', 'кино', 'книги']):
                relevance_score += 5

        # Проверка описания
        if club.description and any(word in club.description.lower() for word in user_message_lower.split()[:5]):
            relevance_score += 3

        # Проверка деятельности
        if club.activities and any(word in club.activities.lower() for word in user_message_lower.split()[:5]):
            relevance_score += 2

        if relevance_score > 0:
            relevant_clubs.append({
                'id': str(club.id),
                'name': club.name,
                'description': club.description[:150] + '...' if len(club.description) > 150 else club.description,
                'city': club.city.name if club.city else 'Не указан',
                'category': club.category.name if club.category else 'Не указана',
                'score': relevance_score
            })

    # Сортировка по релевантности
    relevant_clubs.sort(key=lambda x: x['score'], reverse=True)
    return relevant_clubs[:5]

def generate_ai_response(user_message, relevant_clubs, user_id):
    """Генерация AI ответа на основе контекста"""

    # Определение типа запроса
    user_message_lower = user_message.lower()

    if any(word in user_message_lower for word in ['создать', 'сделать', 'новый', 'club', 'клуб']):
        return handle_club_creation_request(user_message)

    elif any(word in user_message_lower for word in ['рекоменд', 'поиск', 'найти', 'подскаж', 'что посмотреть', 'найди', 'покажи', 'где']):
        return handle_recommendation_request(user_message, relevant_clubs)

    elif any(word in user_message_lower for word in ['привет', 'здравствуй', 'добрый', 'hello', 'hi']):
        return handle_greeting()

    else:
        return handle_general_query(user_message, relevant_clubs)

def handle_greeting():
    """Обработка приветствия"""
    return ("👋 Здравствуйте! Я AI консультант по клубам и мероприятиям.\n\n"
            "Я могу помочь вам:\n"
            "• 🔍 Найти подходящие клубы по вашим интересам\n"
            "• 📍 Посмотреть клубы в вашем городе\n"
            "• 🤝 Создать новый клуб\n"
            "• 💬 Ответить на вопросы о существующих клубах\n\n"
            "Чем могу помочь?")

def handle_club_creation_request(user_message):
    """Обработка запроса на создание клуба"""
    return ("🎉 Отлично! Давайте создадим новый клуб!\n\n"
            "Пожалуйста, ответьте на несколько вопросов:\n\n"
            "1. Какое название вы хотите дать вашему клубу?\n"
            "2. Чем будет заниматься ваш клуб?\n"
            "3. Где будет находиться клуб?\n"
            "4. Для кого предназначен клуб?\n\n"
            "Начнем с названия - как будет называться ваш клуб?")

def handle_recommendation_request(user_message, relevant_clubs):
    """Обработка запроса на рекомендации"""
    if not relevant_clubs:
        return ("😔 К сожалению, я не нашел подходящих клубов по вашему запросу.\n\n"
                "Попробуйте уточнить:\n"
                "• Ваши конкретные интересы\n"
                "• Ваш город или регион\n"
                "• Тип деятельности (музыка, спорт, танцы и т.д.)\n\n"
                "Или расскажите подробнее о том, что вас интересует!")

    response = "🎯 Вот подходящие клубы, которые я нашел:\n\n"
    for i, club in enumerate(relevant_clubs[:3], 1):
        response += (f"{i}. **{club['name']}**\n"
                    f"   📍 {club['city']}\n"
                    f"   📝 {club['description']}\n"
                    f"   💬 Подходит по: {club['score']} критериям\n\n")

    response += ("💬 Хотите больше информации о каком-то из клубов?\n"
                "Или ищете что-то другое?")
    return response

def handle_general_query(user_message, relevant_clubs):
    """Обработка общих запросов"""
    # Простой ответ на основе контекста
    if len(user_message.split()) < 3:
        return ("Я AI консультант по клубам и мероприятиям!\n\n"
                "Задайте мне более конкретный вопрос, например:\n"
                "• 'Найди музыкальные клубы в Алматы'\n"
                "• 'Какие есть спортивные клубы?'\n"
                "• 'Хочу создать танцевальный клуб'\n"
                "• 'Расскажи о клубе Кайрат'")

    # Поиск упоминаний конкретных клубов
    club_names = [club['name'] for club in relevant_clubs[:3]]
    if club_names:
        return (f"Я нашел несколько клубов, которые могут вас заинтересовать: {', '.join(club_names[:2])}.\n\n"
                "Хотите подробную информацию о каком-то из них?\n"
                "Или расскажите, что именно вас интересует?")

    return ("Спасибо за ваш вопрос! Я помогу вам найти подходящие клубы или создать новый.\n\n"
            "Пожалуйста, уточните:\n"
            "• Ваши интересы или хобби\n"
            "• Ваш город\n"
            "• Что именно вы ищете\n\n"
            "Это поможет мне лучше понять и помочь вам! 🤝")