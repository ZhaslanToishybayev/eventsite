from rest_framework import status
from rest_framework.exceptions import APIException


class UserAlreadyInClubException(APIException):
    """
    Исключение, возникающее, когда пользователь пытается присоединиться к клубу, в котором он уже состоит.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Пользователь уже состоит в группе'
    default_code = 'user_already_in_club'


class UserNotInClubException(APIException):
    """
    Исключение, возникающее, когда пользователь не состоит в группе и пытается выполнить действие,
    требующее наличие его в клубе.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Пользователь не состоит в группе'
    default_code = 'user_not_in_club'


class ClubIsInactiveException(APIException):
    """
    Исключение, возникающее, когда происходит попытка выполнить действие с клубом, который не активен.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Данный клуб не активен'
    default_code = 'club_is_inactive'


class UserLikeAlreadyExistsException(APIException):
    """
    Исключение, возникающее, когда пользователь пытается поставить лайк, который уже был установлен.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Лайк уже поставлен'
    default_code = 'user_like_already_exists'


class UserLikeDoesNotExistException(APIException):
    """
    Исключение, возникающее, когда пользователь пытается удалить лайк, которого не существует.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Нет лайка, которого можно было убрать'
    default_code = 'user_like_does_not_exist'


class InvalidClubActionExeption(APIException):
    """
    Исключение, выбрасываемое при попытке выполнить недопустимое действие с клубом.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid club action'
    default_code = 'invalid_club_action'


class ClubAlreadyExistsFestivalException(APIException):
    """
    Исключение, возникающее, когда пользователь пытается вступить в фестиваль, в котором уже состоит.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Вы уже участник фестиваля'
    default_code = 'club_in_festival_already_exists'


class ClubNotExistsFestivalException(APIException):
    """
    Исключение, возникающее, когда пользователь пытается вступить в фестиваль, в котором уже состоит.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Вы уже не являетесь участником фестиваля'
    default_code = 'club_in_festival_not_exists'


class NotClubManagerException(APIException):
    """
    Исключение, выбрасываемое в случае, если пользователь не является менеджером клуба.

    Attributes:
        status_code (int): HTTP-код статуса, возвращаемый в ответе. По умолчанию 400 Bad Request.
        default_detail (str): Сообщение об ошибке, возвращаемое по умолчанию. "Данное действие может выполнить только управляющие клуба".
        default_code (str): Код ошибки, возвращаемый по умолчанию. "not_club_manager".
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Данное действие может выполнить только управляющие клуба'
    default_code = 'not_club_manager'


class FestivalRequestAlreadyExistsException(APIException):
    """
    Исключение, выбрасываемое в случае, если у клуба уже существует запрос на участие в данном фестивале.

    Attributes:
        status_code (int): HTTP-код статуса, возвращаемый в ответе. По умолчанию 400 Bad Request.
        default_detail (str): Сообщение об ошибке, возвращаемое по умолчанию. "У данного клуба уже есть запрос на участие в данном фестивале".
        default_code (str): Код ошибки, возвращаемый по умолчанию. "festival_request_already_exists".
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'У данного клуба уже есть запрос на участие в данном фестивале'
    default_code = 'festival_request_already_exists'


class ClubJoinRequestAlreadyExistsException(APIException):
    """
    Исключение, выбрасываемое в случае, если у клуба уже существует запрос на вступление в приватный клуб.

    Attributes:
        status_code (int): HTTP-код статуса, возвращаемый в ответе. По умолчанию 400 Bad Request.
        default_detail (str): Сообщение об ошибке, возвращаемое по умолчанию. "У данного клуба уже есть запрос на участие в данном фестивале".
        default_code (str): Код ошибки, возвращаемый по умолчанию. "festival_request_already_exists".
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'У данного пользователя уже есть запрос на вступление в клуб'
    default_code = 'club_join_request_already_exists'


class PartnerShipAlreadyExistsException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Данные клубы уже являются партнерами'
    default_code = 'partnership_already_exists'
