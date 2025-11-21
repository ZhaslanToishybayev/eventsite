from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import authentication
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.db import transaction
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.core.exceptions import ValidationError
from django_ratelimit.decorators import ratelimit
from django.utils import timezone
import json
import logging
import time

from ai_consultant.models import ChatSession
from ai_consultant.api.serializers import ChatRequestSerializer, ChatSessionSerializer
from services.ai.chat_business_service import chat_business_service
from ai_consultant.services_v2 import AIConsultantServiceV2
from ai_consultant.services.feedback import FeedbackService
from ai_consultant.services.club_creation import ClubCreationService

User = get_user_model()
logger = logging.getLogger(__name__)


@method_decorator(ensure_csrf_cookie, name='dispatch')
@method_decorator(ratelimit(key='ip', rate='30/m', method='POST', block=True), name='post')
class ChatAPIView(APIView):
    """
    API для работы с чатом ИИ-консультанта
    """
    permission_classes = [permissions.AllowAny]  # Доступно всем

    def __init__(self):
        super().__init__()
        self.chat_service = chat_business_service

    def post(self, request):
        """
        Отправить сообщение и получить ответ от ИИ
        """
        logger.info(f"AI Chat API request from {self.get_client_ip(request)}")

        # Используем бизнес-сервис для обработки сообщения
        response_data, status_code = self.chat_service.process_message(
            request_data=request.data,
            user=request.user if request.user.is_authenticated else None,
            client_ip=self.get_client_ip(request)
        )

        return Response(response_data, status=status_code)

    def get(self, request):
        """
        Получить историю чата с пагинацией

        Query parameters:
        - session_id: ID сессии (обязательный)
        - page: номер страницы (по умолчанию 1)
        - page_size: размер страницы (по умолчанию 50, максимум 200)
        """
        session_id = request.query_params.get('session_id')
        if not session_id:
            return Response(
                {'error': 'session_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Параметры пагинации
        try:
            page = int(request.query_params.get('page', 1))
            page_size = min(
                int(request.query_params.get('page_size', 50)),
                200  # Максимальный размер страницы
            )
            if page < 1:
                page = 1
            if page_size < 1:
                page_size = 50
        except ValueError:
            page = 1
            page_size = 50

        # Используем бизнес-сервис для получения истории
        response_data, status_code = self.chat_service.get_chat_history(
            session_id=session_id,
            user=request.user if request.user.is_authenticated else None,
            page=page,
            page_size=page_size
        )

        return Response(response_data, status=status_code)

    def get_client_ip(self, request):
        """Return client IP address, handling X-Forwarded-For header if present."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip or 'unknown'


@api_view(['GET'])
@permission_classes([permissions.AllowAny])  # Доступно всем
def chat_sessions(request):
    """
    Получить список сессий чата пользователя
    """
    try:
        # Для анонимных пользователей возвращаем пустой список
        if not request.user.is_authenticated:
            return Response({'sessions': []}, status=status.HTTP_200_OK)
            
        ai_service = AIConsultantServiceV2()
        sessions = ai_service.chat_service.get_user_sessions(request.user)
        return Response({'sessions': sessions}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Chat sessions API error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )



@api_view(['GET'])
def welcome_message(request):
    """
    Приветственное сообщение для нового посетителя
    """
    try:
        welcome_message = """🎉 Добро пожаловать в "ЦЕНТР СОБЫТИЙ"!

Я ваш персональный ИИ-ассистент, здесь чтобы помочь вам найти единомышленников, развивать навыки и реализовывать проекты через сообщества.

"ЦЕНТР СОБЫТИЙ" - это экосистема для создания и развития сообществ, где каждый может найти своих людей и вместе делать удивительные вещи.

Чем я могу вам помочь сегодня?"""

        return Response({
            'success': True,
            'message': welcome_message,
            'is_welcome': True,
            'suggestions': [
                'Расскажи о платформе "ЦЕНТР СОБЫТИЙ"',
                'Какие клубы здесь есть?',
                'Как создать свой клуб?',
                'Какие услуги доступны?',
                'Как записаться на интервью?'
            ],
            'next_steps': {
                'title': 'Начните знакомство с платформой',
                'actions': [
                    'Изучите доступные клубы и сообщества',
                    'Оставьте заявку на интервью',
                    'Воспользуйтесь услугами платформы',
                    'Создайте свое сообщество'
                ]
            }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Welcome message API error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])  # Доступно всем
@csrf_exempt
def chat(request):
    """
    Простой эндпоинт чата для виджета - совместимость со старым форматом
    """
    try:
        # Извлекаем данные из запроса
        message = request.data.get('message', '')
        session_id = request.data.get('session_id', None)

        if not message:
            return Response(
                {'error': 'Message is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        ai_service = AIConsultantServiceV2()

        # Если session_id не предоставлен, создаем новую сессию
        if session_id:
            try:
                session = ChatSession.objects.get(id=session_id)
            except ChatSession.DoesNotExist:
                return Response(
                    {'error': 'Invalid session_id'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            # Создаем новую сессию для анонимного пользователя
            session = ChatSession.objects.create(user=None)

        # Отправляем сообщение и получаем ответ
        result = ai_service.send_message(session, message)

        # Форматируем ответ в ожидаемом виде
        response_data = {
            'response': result.get('response', 'Извините, произошла ошибка'),
            'session_id': str(session.id),
            'message_id': result.get('message_id', None),
            'agent': result.get('agent')
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Chat API error: {str(e)}")
        return Response(
            {'error': 'Internal server error', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])  # Доступно всем
@csrf_exempt
def create_chat_session(request):
    """
    Создать новую сессию чата
    """
    try:
        ai_service = AIConsultantServiceV2()

        # Для анонимных пользователей создаем сессию без user
        if request.user.is_authenticated:
            session = ai_service.create_chat_session(request.user)
        else:
            # Создаем анонимную сессию
            session = ChatSession.objects.create(user=None)

        serializer = ChatSessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"Create chat session API error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )



@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_chat_session(request, session_id):
    """
    Удалить (деактивировать) сессию чата
    """
    try:
        session = get_object_or_404(
            ChatSession,
            id=session_id,
            user=request.user,
            is_active=True
        )

        session.is_active = False
        session.save()

        return Response(
            {'message': 'Сессия успешно удалена'},
            status=status.HTTP_200_OK
        )

    except Exception as e:
        logger.error(f"Delete chat session API error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.AllowAny])  # Доступно всем
def user_profile(request):
    """
    Получить информацию о профиле пользователя для ИИ
    """
    try:
        # Для анонимных пользователей возвращаем пустой профиль
        if not request.user.is_authenticated:
            return Response({
                'first_visit_completed': False,
                'welcome_chat_session_created': False,
                'user_interests': '',
                'user_goals': '',
                'user_about': ''
            }, status=status.HTTP_200_OK)
        
        user = request.user

        # Получаем или создаем профиль
        from accounts.models import Profile
        profile, created = Profile.objects.get_or_create(user=user)

        return Response({
            'first_visit_completed': profile.first_visit_completed,
            'welcome_chat_session_created': profile.welcome_chat_session_created,
            'user_interests': profile.interests or '',
            'user_goals': profile.goals_for_life or '',
            'user_about': profile.about or ''
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"User profile API error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )



@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@csrf_exempt
def mark_first_visit(request):
    """
    Отметить первый визит пользователя как завершенный
    """
    try:
        if not request.user.is_authenticated:
            return Response({'error': 'Требуется аутентификация'}, status=401)

        user = request.user

        # Используем User модель вместо Profile
        # Просто возвращаем успех, так как Profile модель не существует
        return Response({
            'message': 'Первый визит отмечен как завершенный',
            'user_id': user.id,
            'username': user.username
              }, status=200)

    except Exception as e:
        logger.error(f"Mark first visit API error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def chat_statistics(request):
    """
    Получить статистику использования чата
    """
    try:
        user = request.user
        sessions = ChatSession.objects.filter(user=user, is_active=True)

        total_sessions = sessions.count()
        total_messages = ChatMessage.objects.filter(session__in=sessions).count()
        total_tokens_used = sum(
            msg.tokens_used for msg in ChatMessage.objects.filter(session__in=sessions)
        )

        return Response({
            'total_sessions': total_sessions,
            'total_messages': total_messages,
            'total_tokens_used': total_tokens_used,
            'average_messages_per_session': total_messages / max(total_sessions, 1)
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Chat statistics API error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def platform_services(request):
    """
    Получить список всех услуг платформы
    """
    try:
        ai_service = AIConsultantServiceV2()
        services = ai_service.get_platform_services()
        return Response({'services': services}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Platform services API error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def services_by_type(request, service_type):
    """
    Получить услуги определенного типа
    """
    try:
        ai_service = AIConsultantServiceV2()
        services = ai_service.get_services_by_type(service_type)
        return Response({'services': services}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Services by type API error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_interview_request(request):
    """
    Создать заявку на интервью
    """
    try:
        ai_service = AIConsultantServiceV2()
        result = ai_service.create_interview_request(request.user, request.data)

        if result['success']:
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Interview request API error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def club_recommendations(request):
    """
    Получить персональные рекомендации клубов для пользователя
    """
    try:
        ai_service = AIConsultantServiceV2()
        limit = int(request.GET.get('limit', 5))

        recommendations = ai_service.get_club_recommendations_for_user(request.user, limit)
        return Response(recommendations, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Club recommendations API error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def search_clubs(request):
    """
    Поиск клубов по ключевым словам
    """
    try:
        ai_service = AIConsultantServiceV2()
        query = request.GET.get('q', '')
        limit = int(request.GET.get('limit', 5))

        if not query:
            return Response(
                {'error': 'Query parameter "q" is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        search_results = ai_service.get_clubs_by_interest_keywords(query, limit)
        return Response(search_results, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Search clubs API error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def development_recommendations(request):
    """
    Получить персональные рекомендации по развитию для пользователя
    """
    try:
        ai_service = AIConsultantServiceV2()
        message = request.GET.get('message', '')

        recommendations = ai_service.get_development_recommendations_for_user(request.user, message)
        return Response(recommendations, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Development recommendations API error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def development_paths(request):
    """
    Получить все доступные дорожки развития
    """
    try:
        from ai_consultant.models import DevelopmentPath

        paths = DevelopmentPath.objects.filter(is_active=True).order_by('order', 'title')
        paths_data = []

        for path in paths:
            paths_data.append({
                'id': str(path.id),
                'title': path.title,
                'description': path.description,
                'target_audience': path.target_audience,
                'duration': path.duration,
                'difficulty_level': path.difficulty_level,
                'is_recommended': path.is_recommended,
                'skills_count': path.skills.count()
            })

        return Response({'paths': paths_data}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Development paths API error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def development_progress(request):
    """
    Получить прогресс развития пользователя
    """
    try:
        ai_service = AIConsultantServiceV2()
        progress = ai_service.get_user_development_progress(request.user)
        return Response(progress, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Development progress API error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_development_plan(request):
    """
    Создать план развития для пользователя
    """
    try:
        path_id = request.data.get('path_id')
        if not path_id:
            return Response(
                {'error': 'Path ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        ai_service = AIConsultantServiceV2()
        result = ai_service.create_development_plan_for_user(request.user, path_id)

        if result['success']:
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Create development plan API error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ===== API ДЛЯ ПОМОЩИ В СОЗДАНИИ КЛУБОВ =====

@api_view(['GET'])
def club_creation_ideas(request):
    """
    Генерирует идеи для создания клубов на основе интересов
    """
    try:
        interests = request.GET.get('interests', '')
        goals = request.GET.get('goals', '')

        if not interests:
            return Response(
                {'error': 'Parameter "interests" is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        club_service = ClubCreationService()
        ideas = club_service.generate_club_ideas(interests, goals)

        return Response({'ideas': ideas}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Club creation ideas API error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def club_name_suggestions(request):
    """
    Генерирует варианты названий для клуба
    """
    try:
        category = request.GET.get('category', '')
        custom_word = request.GET.get('custom_word', '')

        if not category:
            return Response(
                {'error': 'Parameter "category" is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        club_service = ClubCreationService()
        suggestions = club_service.generate_club_name_suggestions(category, custom_word)

        return Response({'suggestions': suggestions}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Club name suggestions API error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def club_description_generator(request):
    """
    Создает описание для клуба на основе параметров
    """
    try:
        category = request.data.get('category', '')
        custom_name = request.data.get('custom_name', '')
        target_audience = request.data.get('target_audience', '')
        activities = request.data.get('activities', '')
        unique_aspect = request.data.get('unique_aspect', '')

        if not category:
            return Response(
                {'error': 'Parameter "category" is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        club_service = ClubCreationService()
        description = club_service.create_club_description(
            category, custom_name, target_audience, activities, unique_aspect
        )

        return Response({'description': description}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Club description generator API error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def club_monetization_ideas(request):
    """
    Генерирует идеи монетизации для клуба
    """
    try:
        category = request.GET.get('category', '')

        if not category:
            return Response(
                {'error': 'Parameter "category" is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        club_service = ClubCreationService()
        ideas = club_service.generate_monetization_ideas(category)

        return Response({'ideas': ideas}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Club monetization ideas API error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def club_action_plan(request):
    """
    Создает пошаговый план для создания клуба
    """
    try:
        user_idea = request.data.get('user_idea', '')
        user_experience = request.data.get('user_experience', '')
        user_resources = request.data.get('user_resources', '')

        if not user_idea:
            return Response(
                {'error': 'Parameter "user_idea" is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        club_service = ClubCreationService()
        plan = club_service.create_action_plan(user_idea, user_experience, user_resources)

        return Response({'plan': plan}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Club action plan API error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ===== API ДЛЯ ОБРАТНОЙ СВЯЗИ =====

@api_view(['POST'])
def create_feedback(request):
    """
    Создает новое обращение обратной связи
    """
    try:
        feedback_service = FeedbackService()

        # Добавляем техническую информацию
        data = request.data.copy()
        data.update({
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'ip_address': request.META.get('REMOTE_ADDR', ''),
            'page_url': request.META.get('HTTP_REFERER', '')
        })

        # Определяем пользователя
        user = request.user if request.user.is_authenticated else None

        result = feedback_service.create_feedback(data, user)

        if result['success']:
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Create feedback API error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def feedback_categories(request):
    """
    Возвращает категории обратной связи
    """
    try:
        from ai_consultant.models import FeedbackCategory

        categories = FeedbackCategory.objects.filter(is_active=True).order_by('order')
        categories_data = []

        for category in categories:
            categories_data.append({
                'id': str(category.id),
                'name': category.name,
                'description': category.description,
                'icon': category.icon,
                'color': category.color,
                'order': category.order
            })

        return Response({'categories': categories_data}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Feedback categories API error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def feedback_history(request):
    """
    Возвращает историю обращений пользователя
    """
    try:
        feedback_service = FeedbackService()
        limit = int(request.GET.get('limit', 10))

        history = feedback_service.get_user_feedback_history(request.user, limit)
        return Response({'history': history}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Feedback history API error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def rate_feedback(request):
    """
    Оценивает полезность ответа на обратную связь
    """
    try:
        feedback_id = request.data.get('feedback_id')
        rating = request.data.get('rating')
        comment = request.data.get('comment', '')

        if not feedback_id or not rating:
            return Response(
                {'error': 'feedback_id and rating are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError()
        except ValueError:
            return Response(
                {'error': 'Rating must be an integer between 1 and 5'},
                status=status.HTTP_400_BAD_REQUEST
            )

        feedback_service = FeedbackService()
        result = feedback_service.rate_feedback_response(feedback_id, rating, comment)

        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Rate feedback API error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def feedback_statistics(request):
    """
    Возвращает статистику по обратной связи
    """
    try:
        feedback_service = FeedbackService()
        stats = feedback_service.get_feedback_statistics()
        return Response(stats, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Feedback statistics API error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ===== API ДЛЯ УСЛУГ ПЛАТФОРМЫ =====

@api_view(['GET'])
def platform_services_list(request):
    """
    Возвращает список всех активных услуг платформы
    """
    try:
        service_manager = PlatformServiceManager()
        services = service_manager.get_all_services()

        services_data = []
        for service in services:
            services_data.append({
                'id': str(service.id),
                'title': service.title,
                'service_type': service.service_type,
                'service_type_display': service.get_service_type_display(),
                'description': service.description,
                'price_info': service.price_info,
                'contact_info': service.contact_info,
                'order': service.order
            })

        return Response({'services': services_data}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Platform services list API error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def services_by_type(request, service_type):
    """
    Возвращает услуги определенного типа
    """
    try:
        service_manager = PlatformServiceManager()
        services = service_manager.get_services_by_type(service_type)

        if not services:
            return Response(
                {'error': f'No services found for type: {service_type}'},
                status=status.HTTP_404_NOT_FOUND
            )

        services_data = []
        for service in services:
            services_data.append({
                'id': str(service.id),
                'title': service.title,
                'description': service.description,
                'price_info': service.price_info,
                'contact_info': service.contact_info,
                'order': service.order
            })

        return Response({
            'service_type': service_type,
            'service_type_display': services[0].get_service_type_display(),
            'services': services_data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Services by type API error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def search_services(request):
    """
    Поиск услуг по ключевым словам
    """
    try:
        query = request.GET.get('q', '')
        if not query:
            return Response(
                {'error': 'Query parameter "q" is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        service_manager = PlatformServiceManager()
        services = service_manager.search_services(query)

        services_data = []
        for service in services:
            services_data.append({
                'id': str(service.id),
                'title': service.title,
                'service_type': service.service_type,
                'service_type_display': service.get_service_type_display(),
                'description': service.description,
                'price_info': service.price_info,
                'contact_info': service.contact_info
            })

        return Response({
            'query': query,
            'results': services_data,
            'count': len(services_data)
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Search services API error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def similar_services(request, service_id):
    """
    Возвращает похожие услуги
    """
    try:
        service_manager = PlatformServiceManager()
        service = service_manager.get_service_by_id(str(service_id))

        if not service:
            return Response(
                {'error': 'Service not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        similar_services = service_manager.get_similar_services(service)

        services_data = []
        for similar_service in similar_services:
            services_data.append({
                'id': str(similar_service.id),
                'title': similar_service.title,
                'description': similar_service.description,
                'price_info': similar_service.price_info,
                'contact_info': similar_service.contact_info
            })

        return Response({
            'original_service': {
                'id': str(service.id),
                'title': service.title,
                'service_type_display': service.get_service_type_display()
            },
            'similar_services': services_data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Similar services API error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_service_request(request):
    """
    Создает заявку на услугу
    """
    try:
        service_id = request.data.get('service_id')
        request_details = request.data.get('details', '')

        if not service_id:
            return Response(
                {'error': 'service_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        service_manager = PlatformServiceManager()
        result = service_manager.create_service_request(
            user=request.user,
            service_id=service_id,
            request_data={
                'details': request_details,
                'user_info': {
                    'name': request.user.get_full_name() or request.user.username,
                    'email': request.user.email,
                    'phone': getattr(request.user.profile, 'phone', '') if hasattr(request.user, 'profile') else ''
                }
            }
        )

        if result['success']:
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Create service request API error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# =========================
# Студия интервью
# =========================

from ai_consultant.services.interview import InterviewStudioService


@api_view(['GET'])
def interview_types(request):
    """
    Возвращает доступные типы интервью
    """
    try:
        interview_service = InterviewStudioService()
        types = interview_service.get_interview_types()

        return Response({
            'interview_types': types,
            'total_count': len(types)
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Interview types API error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_interview_requests(request):
    """
    Возвращает заявки пользователя на интервью
    """
    try:
        interview_service = InterviewStudioService()
        requests = interview_service.get_user_interview_requests(request.user)

        return Response({
            'interview_requests': requests,
            'total_count': len(requests)
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"User interview requests API error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def interview_preparation_guide(request):
    """
    Возвращает руководство по подготовке к интервью
    """
    try:
        interview_type = request.GET.get('type', 'general')

        interview_service = InterviewStudioService()
        guide = interview_service.get_preparation_guide(interview_type)

        return Response(guide, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Interview preparation guide API error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def interview_statistics(request):
    """
    Возвращает статистику по заявкам на интервью
    """
    try:
        interview_service = InterviewStudioService()
        stats = interview_service.get_interview_statistics()

        return Response(stats, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Interview statistics API error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def ai_monitoring_stats(request):
    """
    Возвращает детальную статистику мониторинга AI
    Только для администраторов
    """
    try:
        # Получаем базовую статистику
        daily_stats = ai_monitor.get_daily_stats()

        # Дополнительная статистика
        return Response({
            'daily_stats': daily_stats,
            'health_check': {
                'status': 'healthy',
                'timestamp': timezone.now().isoformat()
            },
            'configuration': {
                'openai_model': settings.OPENAI_MODEL,
                'ai_consultant_enabled': settings.AI_CONSULTANT_ENABLED,
                'max_history_messages': settings.AI_CONSULTANT_MAX_HISTORY_MESSAGES,
                'rate_limit': '30 requests per minute per IP'
            }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"AI monitoring stats error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def system_health_check(request):
    """
    API для проверки здоровья системы
    """
    try:
        from django.db import connection
        from django.core.cache import cache

        # Проверка базы данных
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = 'healthy'

        # Проверка кэша
        cache.set('health_check', 'ok', 10)
        cache_status = 'healthy' if cache.get('health_check') == 'ok' else 'unhealthy'

        # Проверка AI сервиса
        ai_status = 'healthy'  # Пока используем статический ответ

        # Общий статус
        overall_status = 'healthy' if all([
            db_status == 'healthy',
            cache_status == 'healthy',
            ai_status == 'healthy'
        ]) else 'unhealthy'

        return Response({
            'overall_status': overall_status,
            'components': {
                'database': db_status,
                'cache': cache_status,
                'ai_service': ai_status
            },
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK if overall_status == 'healthy' else status.HTTP_503_SERVICE_UNAVAILABLE)

    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return Response({
            'overall_status': 'unhealthy',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)