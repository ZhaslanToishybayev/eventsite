from django.urls import reverse
from django.views import generic
from django.contrib.auth.mixins import PermissionRequiredMixin
from clubs.models import Club, ClubGalleryPhoto
from clubs.forms import AddGalleryPhotoForm
from clubs.mixins import ClubRelatedObjectCreateMixin


class ClubPhotoGalleryView(generic.ListView):
    """
    View для отображения фотогалереи клуба.

    Этот класс обрабатывает отображение списка фотографий в галерее клуба. Фотографии пагинируются по 40 на странице.
    Также устанавливается заголовок страницы и добавляется объект клуба в контекст шаблона.

    Атрибуты:
        model (models.Model): Модель фотографии клуба для отображения.
        context_object_name (str): Имя объекта контекста для шаблона.
        template_name (str): Путь к шаблону страницы с фотогалереей клуба.
        paginate_by (int): Количество фотографий на одной странице.
    """

    model = ClubGalleryPhoto
    context_object_name = 'photos'
    template_name = 'clubs/club_photogallery.html'
    paginate_by = 40

    def get_context_data(self, **kwargs):
        """
        Добавляет дополнительный контекст в шаблон страницы с фотогалереей клуба.

        Добавляет в контекст название страницы и объект клуба.

        Параметры:
            **kwargs: Дополнительные аргументы для контекста.

        Возвращает:
            dict: Контекст для рендеринга шаблона, включая название страницы и объект клуба.
        """
        ctx = super().get_context_data(**kwargs)
        club = Club.objects.get(id=self.kwargs.get('pk'))
        ctx['page_title'] = f'{club} - Фотогалерея'
        ctx['club'] = club
        return ctx

    def get_queryset(self):
        """
        Возвращает отфильтрованный список фотографий клуба.

        Фильтрует фотографии по клубу, используя идентификатор клуба из URL.

        Параметры:
            None

        Возвращает:
            QuerySet: Список фотографий, относящихся к указанному клубу.
        """
        club = Club.objects.get(id=self.kwargs.get('pk'))
        return self.model.objects.filter(club=club)


class ClubAddPhotoView(ClubRelatedObjectCreateMixin, PermissionRequiredMixin, generic.CreateView):
    """
    View для добавления фотографии в галерею клуба.

    Этот класс обрабатывает форму для добавления новой фотографии в галерею клуба. При успешной отправке формы
    пользователя перенаправляют на страницу галереи клуба.

    Атрибуты:
        model (models.Model): Модель фотографии клуба для создания.
        form_class (forms.Form): Форма для добавления фотографии в галерею.
        template_name (str): Путь к шаблону страницы добавления фотографии.
    """

    model = ClubGalleryPhoto
    form_class = AddGalleryPhotoForm
    template_name = 'clubs/club_add_photo.html'

    def get_success_url(self):
        """
        Возвращает URL для перенаправления после успешного добавления фотографии.

        Использует метод get_club() из миксина для получения URL галереи клуба.

        Параметры:
            None

        Возвращает:
            str: URL для перенаправления на страницу галереи клуба после успешного добавления фотографии.
        """
        return self.get_club().get_gallery_url()


class galleryForClubsDeleteView(PermissionRequiredMixin, generic.DeleteView):
    """
    View для удаления фото из галереи для клуба.

    Этот класс отображает страницу подтверждения удаления услуги и обрабатывает её удаление.

    Атрибуты:
        model (models.Model): Модель фото из галереи для клуба.
        template_name (str): Путь к шаблону страницы подтверждения удаления фото из галереи клуба.

    Методы:
        has_permission():
            Проверяет, имеет ли текущий пользователь права для удаления фото из галереи клуба.

        get_success_url():
            Определяет URL для перенаправления после успешного удаления фото из галереи клуба.

        get_context_data(**kwargs):
            Добавляет дополнительную информацию о фото из галереи в контекст.
    """

    model = ClubGalleryPhoto
    template_name = 'clubs/object_delete_confirm.html'

    def has_permission(self):
        """
        Проверяет, имеет ли текущий пользователь разрешение на удаление фото из галереи клуба.

        Параметры:
            None

        Возвращает:
            bool: True, если пользователь является менеджером клуба, иначе False.
        """
        return self.request.user in self.get_object().club.managers.all()

    def get_success_url(self):
        """
        Возвращает URL для перенаправления после успешного удаления фото из галереи клуба.

        Параметры:
            None

        Возвращает:
            str: URL профиля пользователя после успешного удаления фото из галереи клуба.
        """
        return reverse('club_photogallery', kwargs={'pk': self.get_object().club.pk})

    def get_context_data(self, **kwargs):
        """
        Добавляет дополнительный контекст на страницу подтверждения удаления фото из галереи клуба.

        Добавляет в контекст имя и идентификатор объекта, а также URL действия удаления.

        Параметры:
            **kwargs: Дополнительные аргументы для контекста.

        Возвращает:
            dict: Контекст для рендеринга шаблона, включая имя объекта и URL действия удаления.
        """
        context = super().get_context_data(**kwargs)
        context['object_name'] = f'выбранное фото клуба'
        context['object_id'] = self.object.pk
        context['action_url'] = 'photogallery_delete'
        return context


class ClubPhotoDeleteView(PermissionRequiredMixin, generic.DeleteView):
    model = ClubGalleryPhoto

    def has_permission(self):
        return self.get_club().managers.filter(id=self.request.user.id).exists()

    def get_club(self):
        return Club.objects.get(id=self.kwargs.get('pk'))

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER')
