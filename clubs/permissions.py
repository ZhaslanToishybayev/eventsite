from rest_framework import permissions


class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """
    Разрешение, позволяющее только аутентифицированным пользователям выполнять операции записи.

    Если запрос имеет метод только для чтения (GET, HEAD, OPTIONS), разрешение будет предоставлено.
    В противном случае разрешение будет предоставлено только аутентифицированным пользователям.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated


class ClubPermission(IsAuthenticatedOrReadOnly):
    """
    Разрешение для операций над объектами клубов.

    Разрешает только менеджерам клуба выполнять операции записи (удаление, обновление, частичное обновление).
    """
    def has_object_permission(self, request, view, obj):
        if view.action in ('destroy', 'update', 'partial_update'):
            return obj.managers.filter(id=request.user.id).exists()
        if obj.is_private:
            return obj.members.filter(id=request.user.id).exists()
        return True


class ClubObjectsPermission(IsAuthenticatedOrReadOnly):
    """
    Разрешение для операций над объектами, относящимися к клубу.

    Разрешает только менеджерам клуба выполнять операции записи (удаление, обновление, частичное обновление)
    над объектами, связанными с клубом.
    """
    def has_object_permission(self, request, view, obj):
        if view.action in ('destroy', 'update', 'partial_update'):
            return request.user in obj.club.managers.filter(id=request.user.id).exists()
        return True


class IsSuperUserOrReadOnly(permissions.BasePermission):
    """
    Разрешение, позволяющее только суперпользователям выполнять небезопасные методы.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_superuser


class IsClubManager(permissions.BasePermission):
    """
    Разрешение, проверяющее, является ли пользователь менеджером клуба.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        try:
            return obj.club.managers.filter(id=request.user.id).exists()
        except AttributeError:
            return obj.managers.filter(id=request.user.id).exists()


class ClubJoinRequestPermission(permissions.BasePermission):
    """
    Разрешение для обработки запросов на вступление в клуб.
    """
    def has_object_permission(self, request, view, obj):
        if view.action == 'destroy':
            return request.user == obj.user
        if view.action == 'request_action':
            return obj.club.managers.filter(id=request.user.id).exists()
        return True
