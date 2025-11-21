from datetime import datetime

from django.db.models import Q
from rest_framework.filters import OrderingFilter
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework import mixins as drf_mixins
from rest_framework import permissions as drf_permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


from clubs import filtersets
from clubs.api import serializers
from clubs.api import exceptions
from clubs import models
from clubs import permissions
from clubs import services
from clubs import mixins
from clubs.models import ClubJoinRequest


class ClubViewSet(mixins.ClubActionSerializerMixin, viewsets.ModelViewSet):
    """
    ViewSet для управления клубами.

    Данный ViewSet предоставляет стандартные действия CRUD для модели Club,
    а также пользовательское действие `club_action`.

    Атрибуты:
        queryset (QuerySet): Базовый набор данных для этого ViewSet-а, включающий только активные клубы.
        permission_classes (tuple): Классы разрешений, применяемые к этому ViewSet-у.
        ACTION_SERIALIZERS (dict): Словарь, который сопоставляет действия с соответствующими сериализаторами.
        serializer_class (Serializer): Сериализатор, используемый по умолчанию для действий, не указанных в ACTION_SERIALIZERS.
    """
    queryset = models.Club.objects.filter(is_active=True)
    permission_classes = (permissions.ClubPermission,)
    ACTION_SERIALIZERS = {
        'club_action': serializers.ClubActionSerializer,
        'create': serializers.ClubCreateSerializer,
        'update': serializers.ClubUpdateSerializer,
        'retrieve': serializers.ClubDetailSerializer,
        'join_requests': serializers.ClubJoinRequestSerializer,
    }
    serializer_class = serializers.ClubListSerializer
    filterset_class = filtersets.ClubFilter
    services = services.ClubServices
    filter_backends = [OrderingFilter,]

    @action(detail=True, methods=['post'], permission_classes=(IsAuthenticated,))
    def club_action(self, request, **kwargs):
        """
        Пользовательское действие для выполнения определенных операций с клубом.

        Параметры:
            request (Request): Объект запроса с данными.
            **kwargs: Дополнительные аргументы.

        Возвращает:
            Response: HTTP-ответ с статусом 204 (No Content) при успешном выполнении действия.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        club = self.get_object()
        action_name = serializer.validated_data['action']
        getattr(self.services, action_name.value)(club, request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'], permission_classes=(permissions.IsClubManager,))
    def join_requests(self, request, **kwargs):
        queryset = models.ClubJoinRequest.objects.filter(club=self.get_object())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_queryset(self):
        """
        Возвращает набор данных для данного ViewSet-а.

        В зависимости от действия, возвращает оптимизированный queryset с использованием
        select_related и prefetch_related для уменьшения количества запросов к базе данных.

        Возвращает:
            QuerySet: Набор данных для текущего действия.
        """
        queryset = super().get_queryset()
        if self.action == 'retrieve':
            return (
                queryset
                .select_related('category', 'city', 'creater')
                .prefetch_related(
                    'members',
                    'partners',
                    'likes',
                    'managers',
                    'gallery_photos',
                    'services__images',
                    'posts'
                )
            )
        elif self.action == 'list':
            return queryset.select_related('category', 'city')
        return queryset


class ClubServiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления услугами клубов.

    Данный ViewSet позволяет выполнять стандартные операции CRUD (создание, чтение, обновление, удаление)
    для модели ClubService, предоставляя RESTful API для управления услугами клубов.

    Атрибуты:
        queryset (QuerySet): Базовый набор данных для этого ViewSet-а, включающий все услуги клубов.
        permission_classes (tuple): Классы разрешений, применяемые для проверки прав доступа к операциям с услугами клубов.
        serializer_class (Serializer): Сериализатор для преобразования данных модели ClubService в JSON.
    """
    queryset = models.ClubService.objects.all()
    permission_classes = (permissions.ClubObjectsPermission,)
    serializer_class = serializers.ClubServiceSerializer

    @action(detail=True, methods=['get'])
    def images(self):
        images = models.ClubServiceImage.objects.filter(service=self.get_object())
        serializer = serializers.ClubServiceImageSerializer(images, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ClubServiceImageViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ClubServiceImageSerializer
    queryset = models.ClubServiceImage.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_authenticated:
            return qs.filter(service__club__managers=self.request.user)
        return qs


class ClubEventViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления событиями клубов.

    Этот ViewSet предоставляет возможность управлять событиями клубов, включая создание, чтение, обновление и удаление.

    Атрибуты:
        queryset (QuerySet): Базовый набор данных для этого ViewSet-а, включающий все будущие события клубов.
        permission_classes (tuple): Классы разрешений, применяемые для проверки прав доступа к операциям с событиями клубов.
        serializer_class (Serializer): Сериализатор для преобразования данных модели ClubEvent в JSON.
    """
    queryset = models.ClubEvent.objects.filter(start_datetime__gte=datetime.now())
    permission_classes = (permissions.ClubObjectsPermission, )
    serializer_class = serializers.ClubEventSerializer


class ClubAdsViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления рекламными объявлениями клубов.

    Данный ViewSet позволяет выполнять стандартные операции CRUD (создание, чтение, обновление, удаление)
    для модели ClubAds, предоставляя RESTful API для управления рекламными объявлениями клубов.

    Атрибуты:
        queryset (QuerySet): Базовый набор данных для этого ViewSet-а, включающий все рекламные объявления клубов.
        permission_classes (tuple): Классы разрешений, применяемые для проверки прав доступа к операциям с рекламными объявлениями клубов.
        serializer_class (Serializer): Сериализатор для преобразования данных модели ClubAds в JSON.
    """
    queryset = models.ClubAds.objects.all()
    permission_classes = (permissions.ClubObjectsPermission, )
    serializer_class = serializers.ClubAdsSerializer


class ClubCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для просмотра категорий клубов.

    Этот ViewSet предоставляет только чтение (GET) данных о категориях клубов.

    Атрибуты:
        queryset (QuerySet): Базовый набор данных для этого ViewSet-а, включающий только активные категории клубов.
        serializer_class (Serializer): Сериализатор для преобразования данных модели ClubCategory в JSON.
    """
    queryset = models.ClubCategory.objects.filter(is_active=True)
    serializer_class = serializers.ClubCategorySerializer


class ClubCityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для просмотра городов.

    Этот ViewSet предоставляет только чтение (GET) данных о городах.

    Атрибуты:
        queryset (QuerySet): Базовый набор данных для этого ViewSet-а, включающий все города.
        serializer_class (Serializer): Сериализатор для преобразования данных модели City в JSON.
    """
    queryset = models.City.objects.all()
    serializer_class = serializers.ClubCitySerializer


class ClubGalleryPhotoViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления фотографиями галереи клубов.

    Этот ViewSet предоставляет возможность выполнять стандартные операции CRUD (создание, чтение, обновление, удаление)
    для модели ClubGalleryPhoto, позволяя управлять фотографиями галереи клубов через RESTful API.

    Атрибуты:
        queryset (QuerySet): Базовый набор данных для этого ViewSet-а, включающий все фотографии галереи клубов.
        permission_classes (tuple): Классы разрешений, применяемые для проверки прав доступа к операциям с фотографиями галереи клубов.
        serializer_class (Serializer): Сериализатор для преобразования данных модели ClubGalleryPhoto в JSON.
    """
    queryset = models.ClubGalleryPhoto.objects.all()
    permission_classes = (permissions.ClubObjectsPermission,)
    serializer_class = serializers.ClubGalleryPhotoSerializer


class FestivalViewSet(mixins.ClubActionSerializerMixin, viewsets.ModelViewSet):
    """
    ViewSet для управления объектами Festival.

    Этот ViewSet предоставляет возможность выполнять стандартные операции CRUD (создание, чтение, обновление, удаление)
    для модели Festival, позволяя управлять фестивалями через RESTful API.

    Помимо стандартных операций CRUD, ViewSet предоставляет следующие действия:
    - festival_action: Выполнение действия (join, leave) с клубом на фестивале.

    Атрибуты:
        queryset: QuerySet всех фестивалей.
        ACTION_SERIALIZERS: Словарь с сериализаторами для различных действий.
        serializer_class: Сериализатор по умолчанию для создания или обновления фестиваля.
        permission_classes: Кортеж с классами разрешений, применяемых ко всем действиям.
    """
    queryset = models.Festival.objects.all()
    ACTION_SERIALIZERS = {
        'list': serializers.FestivalListSerializer,
        'retrieve': serializers.FestivalRetrieveSerializer,
        'festival_action': serializers.FestivalActionSerializer,
    }
    serializer_class = serializers.FestivalCreateOrUpdateSerializer
    permission_classes = (permissions.IsSuperUserOrReadOnly,)
    services = services.FestivalServices

    @action(detail=True, methods=['post'], permission_classes=[drf_permissions.IsAuthenticated])
    def festival_action(self, request, *args, **kwargs):
        """
        Выполняет действие join или leave с клубом на фестивале.

        Доступные действия:
        - join: Создает объект запроса FestivalParticipationRequest.
        - leave: Удалить клуб из фестиваля.

        Args:
            request: HTTP-запрос.
            *args: Дополнительные аргументы.
            **kwargs: Дополнительные именованные аргументы.

        Returns:
            Response: HTTP-ответ с кодом состояния 204 (No Content) в случае успешного выполнения действия.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        festival = self.get_object()
        club = serializer.validated_data.get('club')
        if not club.managers.filter(id=request.user.id).exists():
            raise exceptions.NotClubManagerException
        action_name = serializer.validated_data.get('action')
        getattr(self.services, action_name.value)(festival, club)
        return Response(status=status.HTTP_204_NO_CONTENT)


class FestivalParticipationRequestViewSet(drf_mixins.ListModelMixin,
                                          drf_mixins.RetrieveModelMixin,
                                          viewsets.GenericViewSet):
    """
    ViewSet для управления объектами FestivalParticipationRequest.

    Этот ViewSet предоставляет возможность выполнять стандартные операции чтения (list, retrieve)
    для модели FestivalParticipationRequest, позволяя управлять запросами на участие в фестивалях через RESTful API.

    Помимо стандартных операций чтения, ViewSet предоставляет следующее действие:
    - request_action: Выполнение действия ('approve', 'reject') с запросом на участие в фестивале.

    Атрибуты:
        permission_classes: Кортеж с классами разрешений, применяемых ко всем действиям.
        queryset: QuerySet всех запросов на участие в фестивалях.
    """
    permission_classes = (permissions.IsSuperUserOrReadOnly,)
    queryset = models.FestivalParticipationRequest.objects.all()
    services = services.FestivalRequestServices

    @action(detail=True, methods=['post'], permission_classes=[drf_permissions.IsAuthenticated])
    def request_action(self, request, *args, **kwargs):
        """
        Выполняет действие с запросом на участие в фестивале.

        Доступные действия:
        - approve: Одобрить запрос на участие в фестивале.
        - reject: Отклонить запрос на участие в фестивале.

        Args:
            request: HTTP-запрос.
            *args: Дополнительные аргументы.
            **kwargs: Дополнительные именованные аргументы.

        Returns:
            Response: HTTP-ответ с кодом состояния 204 (No Content) в случае успешного выполнения действия.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        action_name = serializer.validated_data.get('action')
        festival_request = self.get_object()
        getattr(self.services, action_name.value)(festival_request)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_serializer_class(self):
        """
        Возвращает класс сериализатора, используемого для текущего действия.

        Если действие request_action, используется FestivalRequestActionSerializer,
        иначе используется FestivalRequestSerializer.

        Returns:
            class: Класс сериализатора.
        """
        if self.action == 'request_action':
            return serializers.FestivalRequestActionSerializer
        return serializers.FestivalRequestSerializer


class ClubJoinRequestViewSet(drf_mixins.RetrieveModelMixin,
                             drf_mixins.ListModelMixin,
                             drf_mixins.DestroyModelMixin,
                             viewsets.GenericViewSet):
    """
    Вьюсет для обработки запросов на вступление в клуб. Этот вьюсет поддерживает
    получение, перечисление и удаление запросов на вступление, а также обработку
    пользовательских действий с запросами.

    Разрешения:
        - Требуется, чтобы у пользователя было разрешение ClubJoinRequestPermission.

    Набор запросов:
        - Все объекты ClubJoinRequest.
    """
    permission_classes = (permissions.ClubJoinRequestPermission,)
    queryset = ClubJoinRequest.objects.all()
    services = services.ClubJoinRequestServices

    @action(detail=True, methods=['post'])
    def request_action(self, request, *args, **kwargs):
        """
        Обрабатывает пользовательские действия с запросом на вступление, такие как approve или reject.

        Принимает:
            - request: Объект запроса, содержащий данные для сериализации.

        Действия:
            - Получает объект запроса на вступление.
            - Выполняет действие, указанное в данных запроса.

        Возвращает:
            - HTTP 204 No Content при успешном выполнении действия.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request = self.get_object()
        action_name = serializer.validated_data.get('action')
        getattr(self.services, action_name.value)(request)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_serializer_class(self):
        """
        Определяет класс сериализатора в зависимости от действия.

        Возвращает:
            - ClubJoinRequestActionSerializer, если действие request_action.
            - ClubJoinRequestSerializer для всех остальных случаев.
        """
        if self.action == 'request_action':
            return serializers.ClubJoinRequestActionSerializer
        return serializers.ClubJoinRequestSerializer

    def get_queryset(self):
        """
        Определяет набор запросов, доступных пользователю.

        Возвращает:
            - Запросы, где пользователь является автором или менеджером клуба.
        """
        qs = super().get_queryset()
        return qs.filter(Q(user=self.request.user) | Q(club__managers=self.request.user)).distinct()


class ClubPartnerShipRequestViewSet(mixins.ClubActionSerializerMixin,
                                    viewsets.ModelViewSet):
    serializer_class = serializers.ClubPartnershipRequestSerializer
    queryset = models.ClubPartnerShipRequest.objects.all()
    permission_classes = (drf_permissions.IsAuthenticatedOrReadOnly, )
    ACTION_SERIALIZERS = {
        'request_action': serializers.ClubPartnershipRequestActionSerializer,
    }
    services = services.ClubPartnershipRequestServices

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(
            Q(club_requester__managers=self.request.user) |
            Q(club_accepter__managers=self.request.user)
        ).distinct()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        club_requester = serializer.validated_data.get('club_requester')
        club_accepter = serializer.validated_data.get('club_accepter')
        if not club_requester.managers.filter(id=request.user.id).exists():
            raise exceptions.NotClubManagerException
        if club_accepter.partners.filter(id=club_requester.id).exists():
            raise exceptions.PartnerShipAlreadyExistsException
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        partnership_request = self.get_object()
        if partnership_request.club.managers.filter(id=request.user.id).exists():
            raise exceptions.NotClubManagerException
        partnership_request.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def request_action(self, request, *args, **kwargs):
        partnership_request = self.get_object()
        if not partnership_request.club_accepter.managers.filter(id=request.user.id).exists():
            raise exceptions.NotClubManagerException
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        partnership_request = self.get_object()
        action_name = serializer.validated_data.get('action')
        getattr(self.services, action_name.value)(partnership_request)
