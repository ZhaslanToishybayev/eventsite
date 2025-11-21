"""
Club Business Service
Вынесенная бизнес-логика из clubs/api/views.py и clubs/views/clubs.py
"""

import logging
from typing import Dict, Any, Optional, Tuple, List
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import transaction
from django.utils import timezone
from rest_framework import status

from clubs.models import Club, ClubJoinRequest, ClubManager, ClubPartnershipRequest
from clubs.models import Festival, FestivalRequest
from clubs.services import ClubServices
from clubs import permissions as club_permissions

User = get_user_model()
logger = logging.getLogger(__name__)


class ClubBusinessService:
    """
    Бизнес-логика для управления клубами
    """

    def __init__(self):
        self.club_services = ClubServices()

    def join_club(self, club_id: int, user: User, request_data: Dict[str, Any] = None) -> Tuple[Dict[str, Any], int]:
        """
        Вступление пользователя в клуб

        Returns:
            Tuple[response_data, status_code]
        """
        try:
            club = self._get_club_with_permission_check(club_id, user, action='join')

            # Проверка, не состоит ли пользователь уже в клубе
            if club.members.filter(id=user.id).exists():
                return self._format_error_response(
                    "Вы уже состоите в этом клубе",
                    status.HTTP_400_BAD_REQUEST
                )

            # Проверка, есть ли уже активная заявка
            if ClubJoinRequest.objects.filter(club=club, user=user, status='pending').exists():
                return self._format_error_response(
                    "У вас уже есть активная заявка на вступление в этот клуб",
                    status.HTTP_400_BAD_REQUEST
                )

            # Создание заявки на вступление
            join_request = ClubJoinRequest.objects.create(
                club=club,
                user=user,
                message=request_data.get('message', '') if request_data else '',
                status='pending'
            )

            logger.info(f"User {user.id} requested to join club {club_id}")

            return {
                'message': 'Заявка на вступление отправлена',
                'request_id': join_request.id,
                'status': 'pending'
            }, status.HTTP_201_CREATED

        except ValidationError as e:
            return self._format_error_response(str(e), status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error joining club {club_id}: {e}")
            return self._format_error_response(
                "Ошибка при вступлении в клуб",
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def leave_club(self, club_id: int, user: User) -> Tuple[Dict[str, Any], int]:
        """
        Выход пользователя из клуба

        Returns:
            Tuple[response_data, status_code]
        """
        try:
            club = self._get_club_with_permission_check(club_id, user, action='leave')

            # Проверка, состоит ли пользователь в клубе
            if not club.members.filter(id=user.id).exists():
                return self._format_error_response(
                    "Вы не состоите в этом клубе",
                    status.HTTP_400_BAD_REQUEST
                )

            # Проверка, не является ли пользователь создателем или менеджером
            if club.creater == user or club.managers.filter(user=user).exists():
                return self._format_error_response(
                    "Создатель и менеджеры не могут выйти из клуба",
                    status.HTTP_400_BAD_REQUEST
                )

            # Удаление пользователя из членов клуба
            club.members.remove(user)

            logger.info(f"User {user.id} left club {club_id}")

            return {'message': 'Вы покинули клуб'}, status.HTTP_200_OK

        except ValidationError as e:
            return self._format_error_response(str(e), status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error leaving club {club_id}: {e}")
            return self._format_error_response(
                "Ошибка при выходе из клуба",
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def manage_join_request(self, club_id: int, request_id: int, action: str,
                          user: User, response_data: Dict[str, Any] = None) -> Tuple[Dict[str, Any], int]:
        """
        Управление заявками на вступление в клуб (принять/отклонить)

        Returns:
            Tuple[response_data, status_code]
        """
        try:
            club = self._get_club_with_permission_check(club_id, user, action='manage_requests')

            # Проверка прав на управление заявками
            if not self._can_manage_requests(club, user):
                raise PermissionDenied("У вас нет прав на управление заявками")

            # Получение заявки
            try:
                join_request = ClubJoinRequest.objects.get(
                    id=request_id,
                    club=club,
                    status='pending'
                )
            except ClubJoinRequest.DoesNotExist:
                return self._format_error_response(
                    "Заявка не найдена или уже обработана",
                    status.HTTP_404_NOT_FOUND
                )

            # Обработка заявки
            with transaction.atomic():
                if action == 'accept':
                    join_request.status = 'accepted'
                    join_request.response_message = response_data.get('message', '') if response_data else ''
                    join_request.processed_at = timezone.now()
                    join_request.processed_by = user
                    join_request.save()

                    # Добавление пользователя в члены клуба
                    club.members.add(join_request.user)

                    logger.info(f"Join request {request_id} accepted by {user.id}")

                    return {
                        'message': 'Заявка принята',
                        'user_id': join_request.user.id,
                        'username': join_request.user.username
                    }, status.HTTP_200_OK

                elif action == 'reject':
                    join_request.status = 'rejected'
                    join_request.response_message = response_data.get('message', '') if response_data else ''
                    join_request.processed_at = timezone.now()
                    join_request.processed_by = user
                    join_request.save()

                    logger.info(f"Join request {request_id} rejected by {user.id}")

                    return {
                        'message': 'Заявка отклонена',
                        'user_id': join_request.user.id,
                        'username': join_request.user.username
                    }, status.HTTP_200_OK

                else:
                    return self._format_error_response(
                        "Неверное действие. Используйте 'accept' или 'reject'",
                        status.HTTP_400_BAD_REQUEST
                    )

        except PermissionDenied as e:
            return self._format_error_response(str(e), status.HTTP_403_FORBIDDEN)
        except ValidationError as e:
            return self._format_error_response(str(e), status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error managing join request {request_id}: {e}")
            return self._format_error_response(
                "Ошибка при обработке заявки",
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def create_club_partnership(self, club_id: int, partner_club_id: int,
                               user: User, partnership_data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """
        Создание запроса на партнерство между клубами

        Returns:
            Tuple[response_data, status_code]
        """
        try:
            # Получаем оба клуба
            club = self._get_club_with_permission_check(club_id, user, action='manage_partnership')
            partner_club = self._get_club_with_permission_check(partner_club_id, user, action='view')

            # Проверка прав на управление партнерством
            if not self._can_manage_partnership(club, user):
                raise PermissionDenied("У вас нет прав на управление партнерством")

            # Проверка, что клубы не одинаковые
            if club.id == partner_club.id:
                return self._format_error_response(
                    "Нельзя создать партнерство с тем же клубом",
                    status.HTTP_400_BAD_REQUEST
                )

            # Проверка на существующее партнерство
            if ClubPartnershipRequest.objects.filter(
                club=club,
                partner_club=partner_club,
                status__in=['pending', 'accepted']
            ).exists():
                return self._format_error_response(
                    "Партнерство с этим клубом уже существует или находится на рассмотрении",
                    status.HTTP_400_BAD_REQUEST
                )

            # Создание запроса на партнерство
            partnership_request = ClubPartnershipRequest.objects.create(
                club=club,
                partner_club=partner_club,
                initiated_by=user,
                description=partnership_data.get('description', ''),
                partnership_type=partnership_data.get('partnership_type', 'general'),
                status='pending'
            )

            logger.info(f"Partnership request created: {club_id} -> {partner_club_id} by {user.id}")

            return {
                'message': 'Запрос на партнерство отправлен',
                'request_id': partnership_request.id,
                'status': 'pending'
            }, status.HTTP_201_CREATED

        except PermissionDenied as e:
            return self._format_error_response(str(e), status.HTTP_403_FORBIDDEN)
        except ValidationError as e:
            return self._format_error_response(str(e), status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error creating club partnership: {e}")
            return self._format_error_response(
                "Ошибка при создании партнерства",
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_club_join_requests(self, club_id: int, user: User,
                             status_filter: str = None) -> Tuple[List[Dict[str, Any]], int]:
        """
        Получение заявок на вступление в клуб

        Returns:
            Tuple[requests_list, status_code]
        """
        try:
            club = self._get_club_with_permission_check(club_id, user, action='view_requests')

            # Проверка прав на просмотр заявок
            if not self._can_view_requests(club, user):
                raise PermissionDenied("У вас нет прав на просмотр заявок")

            # Получение заявок
            requests_query = ClubJoinRequest.objects.filter(club=club)

            if status_filter:
                requests_query = requests_query.filter(status=status_filter)

            requests = requests_query.select_related('user', 'processed_by').order_by('-created_at')

            requests_data = []
            for req in requests:
                requests_data.append({
                    'id': req.id,
                    'user_id': req.user.id,
                    'username': req.user.username,
                    'message': req.message,
                    'status': req.status,
                    'created_at': req.created_at.isoformat(),
                    'processed_at': req.processed_at.isoformat() if req.processed_at else None,
                    'processed_by': req.processed_by.username if req.processed_by else None,
                    'response_message': req.response_message
                })

            return requests_data, status.HTTP_200_OK

        except PermissionDenied as e:
            return [], status.HTTP_403_FORBIDDEN
        except ValidationError as e:
            return [], status.HTTP_400_BAD_REQUEST
        except Exception as e:
            logger.error(f"Error getting join requests for club {club_id}: {e}")
            return [], status.HTTP_500_INTERNAL_SERVER_ERROR

    def add_club_manager(self, club_id: int, target_user_id: int,
                        user: User) -> Tuple[Dict[str, Any], int]:
        """
        Добавление менеджера в клуб

        Returns:
            Tuple[response_data, status_code]
        """
        try:
            club = self._get_club_with_permission_check(club_id, user, action='manage_managers')

            # Проверка прав на добавление менеджеров
            if not self._can_manage_managers(club, user):
                raise PermissionDenied("У вас нет прав на управление менеджерами")

            # Получение целевого пользователя
            try:
                target_user = User.objects.get(id=target_user_id)
            except User.DoesNotExist:
                return self._format_error_response(
                    "Пользователь не найден",
                    status.HTTP_404_NOT_FOUND
                )

            # Проверка, не является ли пользователь уже менеджером
            if ClubManager.objects.filter(club=club, user=target_user).exists():
                return self._format_error_response(
                    "Пользователь уже является менеджером этого клуба",
                    status.HTTP_400_BAD_REQUEST
                )

            # Добавление менеджера
            ClubManager.objects.create(
                club=club,
                user=target_user,
                added_by=user,
                role='manager'
            )

            logger.info(f"User {target_user_id} added as manager to club {club_id} by {user.id}")

            return {
                'message': 'Менеджер успешно добавлен',
                'user_id': target_user.id,
                'username': target_user.username
            }, status.HTTP_201_CREATED

        except PermissionDenied as e:
            return self._format_error_response(str(e), status.HTTP_403_FORBIDDEN)
        except ValidationError as e:
            return self._format_error_response(str(e), status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error adding manager to club {club_id}: {e}")
            return self._format_error_response(
                "Ошибка при добавлении менеджера",
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # Вспомогательные методы

    def _get_club_with_permission_check(self, club_id: int, user: User, action: str = 'view') -> Club:
        """Получение клуба с базовой проверкой"""
        try:
            club = Club.objects.get(id=club_id, is_active=True)
            return club
        except Club.DoesNotExist:
            raise ValidationError("Клуб не найден")

    def _can_manage_requests(self, club: Club, user: User) -> bool:
        """Проверка прав на управление заявками"""
        return (
            club.creater == user or
            club.managers.filter(user=user).exists() or
            user.is_staff
        )

    def _can_view_requests(self, club: Club, user: User) -> bool:
        """Проверка прав на просмотр заявок"""
        return self._can_manage_requests(club, user)

    def _can_manage_partnership(self, club: Club, user: User) -> bool:
        """Проверка прав на управление партнерством"""
        return (
            club.creater == user or
            club.managers.filter(user=user).exists() or
            user.is_staff
        )

    def _can_manage_managers(self, club: Club, user: User) -> bool:
        """Проверка прав на управление менеджерами"""
        return club.creater == user or user.is_staff

    def _format_error_response(self, error_message: str, status_code: int) -> Tuple[Dict[str, Any], int]:
        """Формирование ответа с ошибкой"""
        return {
            'error': error_message,
            'timestamp': timezone.now().isoformat()
        }, status_code


# Глобальный экземпляр сервиса
club_business_service = ClubBusinessService()