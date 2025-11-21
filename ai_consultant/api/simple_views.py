"""
Упрощенный AI API для тестирования функционала
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django_ratelimit.decorators import ratelimit
from django.utils import timezone
import json
import logging
import time
import uuid

from ai_consultant.models import ChatSession, ChatMessage
from clubs.models import Club, ClubCategory
from core.monitoring import ai_monitor
from core.security import sanitize_input_data

User = get_user_model()
logger = logging.getLogger(__name__)


def validate_message_content(value):
    """Базовая валидация сообщения"""
    if not value or not value.strip():
        raise ValueError("Сообщение не может быть пустым")
    if len(value.strip()) > 10000:
        raise ValueError("Сообщение слишком длинное")
    return value.strip()


@api_view(['POST'])
@permission_classes([AllowAny])
@ratelimit(key='ip', rate='30/m', method='POST', block=True)
@ensure_csrf_cookie
def simple_chat(request):
    """
    Упрощенный AI чат с поддержкой создания клубов
    """
    start_time = time.time()
    client_ip = request.META.get('REMOTE_ADDR', 'unknown')
    session_id = None
    message = ""

    try:
        # Очищаем входные данные
        sanitized_data = sanitize_input_data(request.data)

        message = sanitized_data.get('message', '').strip()
        session_id = sanitized_data.get('session_id')

        # Валидация сообщения
        try:
            message = validate_message_content(message)
        except ValueError as e:
            return Response({
                'error': str(e),
                'success': False
            }, status=status.HTTP_400_BAD_REQUEST)

        # Получаем или создаем сессию
        if session_id:
            try:
                session = ChatSession.objects.get(id=session_id)
            except ChatSession.DoesNotExist:
                session = ChatSession.objects.create(
                    id=uuid.uuid4(),
                    user=request.user if request.user.is_authenticated else None,
                    title=f"Чат от {timezone.now().strftime('%Y-%m-%d %H:%M')}"
                )
        else:
            session = ChatSession.objects.create(
                id=uuid.uuid4(),
                user=request.user if request.user.is_authenticated else None,
                title=f"Чат от {timezone.now().strftime('%Y-%m-%d %H:%M')}"
            )

        # Сохраняем сообщение пользователя
        user_message = ChatMessage.objects.create(
            session=session,
            content=message,
            is_from_user=True
        )

        # Генерируем ответ ИИ
        ai_response = generate_ai_response(message, request.user)

        # Сохраняем ответ ИИ
        ai_message = ChatMessage.objects.create(
            session=session,
            content=ai_response,
            is_from_user=False
        )

        response_data = {
            'response': ai_response,
            'session_id': str(session.id),
            'message_id': str(ai_message.id),
            'tokens_used': 0,
            'processing_time': f"{time.time() - start_time:.2f}s",
            'success': True,
            'fallback_mode': True
        }

        # Отслеживаем успешный запрос
        ai_monitor.track_request(
            request_data={
                'client_ip': client_ip,
                'session_id': session_id,
                'message': message,
                'user': request.user if request.user.is_authenticated else None
            },
            response_data=response_data,
            processing_time=time.time() - start_time
        )

        return Response({
            'success': True,
            'message': ai_response,
            'response': ai_response,
            'session_id': str(session.id),
            'message_id': str(ai_message.id),
            'tokens_used': 0,
            'processing_time': f"{time.time() - start_time:.2f}s",
            'fallback_mode': True
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Simple chat error: {str(e)}", exc_info=True)

        # Отслеживаем ошибку
        ai_monitor.track_request(
            request_data={'client_ip': client_ip, 'session_id': session_id, 'message': message},
            response_data={},
            processing_time=time.time() - start_time,
            error=e
        )

        return Response({
            'error': 'Internal server error',
            'success': False,
            'message': 'Произошла ошибка при обработке запроса. Попробуйте еще раз.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def generate_ai_response(message, user=None):
    """
    Генерирует умный ответ на основе ключевых слов в сообщении
    """
    message_lower = message.lower()

    # Приветствие
    if any(word in message_lower for word in ['привет', 'здравствуй', 'хай', 'hello']):
        return """Привет! Я ваш AI-консультант платформы "ЦЕНТР СОБЫТИЙ"!

Я могу помочь вам:
* Найти интересные клубы и сообщества
* Создать свой клуб
* Узнать о функциях платформы
* Развить ваши навыки
* Ответить на любые вопросы

Как я могу помочь вам сегодня?"""

    # Создание клуба
    elif any(word in message_lower for word in ['создать клуб', 'новый клуб', 'создание клуба', 'хочу создать клуб', 'как создать клуб']):
        return """Создание клуба на платформе "ЦЕНТР СОБЫТИЙ"

Для создания клуба вам потребуется:

Основная информация:
* Название клуба
* Описание (что делает ваш клуб)
* Категория (спорт, творчество, технологии и т.д.)
* Логотип (изображение)

Детали:
* Приватный или публичный клуб
* Правила участия
* Планы на мероприятия

Как создать:
1. Войдите в свой аккаунт на сайте
2. Нажмите "Создать клуб"
3. Заполните все необходимые поля
4. Загрузите логотип
5. Опубликуйте клуб

Совет: Чем подробнее описание, тем больше людей заинтересуется вашим клубом!

Хотите, чтобы я помог составить описание для вашего клуба?"""

    # Поиск клубов
    elif any(word in message_lower for word in ['найти клуб', 'поиск клубов', 'интересные клубы', 'какие клубы']):
        clubs = Club.objects.filter(is_active=True).order_by('-members_count')[:5]
        if clubs:
            response = "Популярные клубы на платформе:\n\n"
            for i, club in enumerate(clubs, 1):
                response += f"{i}. {club.name}\n"
                response += f"   Участников: {club.members_count}\n"
                response += f"   {club.description[:100]}...\n"
                if club.category:
                    response += f"   Категория: {club.category.name}\n"
                response += "\n"
            response += f"\nВсего активных клубов: {Club.objects.filter(is_active=True).count()}"
            return response
        else:
            return "Пока нет активных клубов. Станьте первым, кто создаст сообщество!"

    # Категории
    elif any(word in message_lower for word in ['категории', 'тематики', 'направления']):
        categories = ClubCategory.objects.filter(is_active=True)
        if categories:
            response = "Доступные категории клубов:\n\n"
            for category in categories:
                club_count = Club.objects.filter(category=category, is_active=True).count()
                response += f"* {category.name} ({club_count} клубов)\n"
            return response
        else:
            return "Категории пока не настроены."

    # Функции платформы
    elif any(word in message_lower for word in ['функции', 'возможности', 'что умеет', 'функционал']):
        return """Основные функции платформы "ЦЕНТР СОБЫТИЙ":

Управление клубами:
* Создание и настройка клубов
* Управление участниками
* Организация мероприятий
* Партнерство между клубами

Личный кабинет:
* Профиль пользователя
* Настройки приватности
* История активности
* Достижения

AI-консультант:
* Помощь в создании клубов
* Поиск интересных сообществ
* Рекомендации по развитию
* 24/7 поддержка

Чем хотите воспользоваться?"""

    # Помощь
    elif any(word in message_lower for word in ['помощь', 'help', 'как пользоваться']):
        return """Нужна помощь? Я здесь, чтобы помочь!

Что я могу сделать:
* Подсказать, как создать клуб
* Помочь найти интересные сообщества
* Объяснить функции платформы
* Дать советы по развитию клуба
* Ответить на любые вопросы

Просто спросите меня что-нибудь!

Например:
* "Как создать спортивный клуб?"
* "Найди клубы про технологии"
* "Расскажи про фестивали"""

    # Фестивали
    elif any(word in message_lower for word in ['фестиваль', 'событие', 'мероприятие']):
        return """Фестивали и события на платформе

Фестивали - это большие мероприятия, где несколько клубов объединяются для представления своих достижений!

Типы фестивалей:
* Спортивные соревнования
* Творческие выставки
* Технологические хакатоны
* Культурные праздники
* Образовательные конференции

Возможности:
* Презентация вашего клуба
* Привлечение новых участников
* Сотрудничество с другими клубами
* Получение наград и признания

Участие:
Следите за объявлениями о предстоящих фестивалях и регистрируйте свой клуб!

Хотите узнать больше о конкретном типе фестивалей?"""

    # По умолчанию
    else:
        return f"""Я получил ваше сообщение: "{message}"

Я AI-консультант платформы "ЦЕНТР СОБЫТИЙ" и здесь, чтобы помочь вам!

Попробуйте спросить:
* "Создай клуб" - я помогу создать сообщество
* "Найди клубы" - покажу интересные группы
* "Расскажи о функциях" - объясню возможности платформы
* "Помощь" - подскажу, с чего начать

Чем конкретно я могу вам помочь сегодня?"""


@api_view(['GET'])
@permission_classes([AllowAny])
def simple_welcome(request):
    """
    Простое приветствие
    """
    return Response({
        'message': "Добро пожаловать в AI-консультант платформы 'ЦЕНТР СОБЫТИЙ'!",
        'suggestions': [
            'Создать клуб',
            'Найти интересные клубы',
            'Рассказать о функциях платформы',
            'Помощь и поддержка'
        ]
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def simple_status(request):
    """
    Статус AI сервиса
    """
    return Response({
        'status': 'working',
        'mode': 'fallback',
        'features': [
            'Chat processing',
            'Club creation assistance',
            'Club search',
            'Platform help'
        ]
    })