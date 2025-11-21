from .models import ClubCategory, Club


class ClubActionSerializerMixin:
    """
    Миксин, который позволяет использовать разные сериализаторы для разных действий в ViewSet-ах.

    Этот миксин позволяет определять разные сериализаторы для различных действий (например, 'create', 'update',
    'retrieve', и т. д.) внутри ViewSet-ов. Для этого необходимо создать атрибут класса ACTION_SERIALIZERS,
    который сопоставляет действия с соответствующими сериализаторами.

    Атрибуты:
        ACTION_SERIALIZERS (dict): Словарь, который сопоставляет действия с соответствующими сериализаторами.

    Пример использования:
        class MyViewSet(ClubActionSerializerMixin, viewsets.ModelViewSet):
            ACTION_SERIALIZERS = {
                'create': MyCreateSerializer,
                'update': MyUpdateSerializer,
                'retrieve': MyRetrieveSerializer,
            }
    """

    ACTION_SERIALIZERS = {}

    def get_serializer_class(self):
        """
        Возвращает класс сериализатора для текущего действия.

        Если для текущего действия определен соответствующий сериализатор в атрибуте ACTION_SERIALIZERS,
        возвращается этот сериализатор. В противном случае используется сериализатор, определенный в родительском классе.

        Возвращает:
            Serializer: Класс сериализатора для текущего действия.
        """
        if serializer := self.ACTION_SERIALIZERS.get(self.action):
            return serializer
        return super().get_serializer_class()


class CategoryListMixin:

    def get_categories(self):
        return ClubCategory.objects.filter(is_active=True)


class ClubRelatedObjectCreateMixin(CategoryListMixin):

    def get_club(self):
        return Club.objects.get(id=self.kwargs.get('pk'))

    def get_initial(self):
        initial = super().get_initial()
        initial['club'] = self.get_club()
        return initial

    def has_permission(self):
        return self.get_club().managers.filter(id=self.request.user.id).exists()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f'{self.get_club()} - Добавить {self.model._meta.verbose_name}'
        ctx['categories'] = self.get_categories()
        return ctx
