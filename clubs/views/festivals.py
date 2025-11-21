from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse
from django.views import generic

from clubs import models, forms

class FestivalListView(generic.ListView):
    """
    View для отображения списка фестивалей.

    Этот класс отображает список всех фестивалей с пагинацией.

    Атрибуты:
        model (models.Model): Модель фестиваля для отображения.
        context_object_name (str): Имя объекта контекста для шаблона.
        template_name (str): Путь к шаблону страницы со списком фестивалей.
        paginate_by (int): Количество фестивалей на одной странице.
    """

    model = models.Festival
    context_object_name = 'festivals'
    template_name = 'festivals/list.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        """
        Добавляет дополнительный контекст на страницу со списком фестивалей.

        Добавляет в контекст заголовок страницы.

        Параметры:
            **kwargs: Дополнительные аргументы для контекста.

        Возвращает:
            dict: Контекст для рендеринга шаблона, включая заголовок страницы.
        """
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'ФЕСТИВАЛИ'
        return context


class FestivalDetailView(generic.DetailView):
    """
    View для отображения подробностей фестиваля.

    Этот класс отображает страницу с подробностями выбранного фестиваля. Также отображает клубы, созданные пользователем, если он авторизован.

    Атрибуты:
        model (models.Model): Модель фестиваля для отображения.
        context_object_name (str): Имя объекта контекста для шаблона.
        template_name (str): Путь к шаблону страницы с деталями фестиваля.
    """

    model = models.Festival
    context_object_name = 'festival'
    template_name = 'festivals/detail.html'

    def get_context_data(self, **kwargs):
        """
        Добавляет дополнительный контекст на страницу с деталями фестиваля.

        Добавляет в контекст название фестиваля и клубы, созданные пользователем (если он авторизован).

        Параметры:
            **kwargs: Дополнительные аргументы для контекста.

        Возвращает:
            dict: Контекст для рендеринга шаблона, включая название фестиваля и клубы пользователя.
        """
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['page_title'] = self.get_object().name
        if user.is_authenticated:
            context['created_clubs'] = user.managed_clubs.values()
        return context


class FestivalCreateView(PermissionRequiredMixin, generic.CreateView):
    """
    View для создания нового фестиваля.

    Этот класс обрабатывает создание нового фестиваля. Доступ к созданию фестиваля имеют только пользователи с правами администратора.

    Атрибуты:
        model (models.Model): Модель фестиваля для создания.
        form_class (forms.Form): Форма для создания фестиваля.
        template_name (str): Путь к шаблону страницы создания фестиваля.
    """

    model = models.Festival
    form_class = forms.FestivalForm
    template_name = 'festivals/create_update.html'

    def get_context_data(self, **kwargs):
        """
        Добавляет дополнительный контекст на страницу создания фестиваля.

        Добавляет в контекст заголовок страницы.

        Параметры:
            **kwargs: Дополнительные аргументы для контекста.

        Возвращает:
            dict: Контекст для рендеринга шаблона, включая заголовок страницы.
        """
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Новый фестиваль'
        return context

    def has_permission(self):
        """
        Проверяет, имеет ли пользователь права на создание фестиваля.

        Параметры:
            None

        Возвращает:
            bool: True, если пользователь является суперпользователем, иначе False.
        """
        return self.request.user.is_superuser


class FestivalUpdateView(PermissionRequiredMixin, generic.UpdateView):
    """
    View для обновления фестиваля.

    Этот класс обрабатывает обновление существующего фестиваля. Доступ к изменению фестиваля имеют только пользователи с правами администратора.

    Атрибуты:
        model (models.Model): Модель фестиваля для обновления.
        form_class (forms.Form): Форма для обновления фестиваля.
        template_name (str): Путь к шаблону страницы обновления фестиваля.
    """

    model = models.Festival
    form_class = forms.FestivalForm
    template_name = 'festivals/create_update.html'

    def get_context_data(self, **kwargs):
        """
        Добавляет дополнительный контекст на страницу обновления фестиваля.

        Добавляет в контекст заголовок страницы.

        Параметры:
            **kwargs: Дополнительные аргументы для контекста.

        Возвращает:
            dict: Контекст для рендеринга шаблона, включая заголовок страницы.
        """
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Изменить фестиваль'
        return context

    def has_permission(self):
        """
        Проверяет, имеет ли пользователь права на изменение фестиваля.

        Параметры:
            None

        Возвращает:
            bool: True, если пользователь является суперпользователем, иначе False.
        """
        return self.request.user.is_superuser


class FestivalDeleteView(PermissionRequiredMixin, generic.DeleteView):
    """
    View для удаления фестиваля.

    Этот класс обрабатывает удаление существующего фестиваля. Доступ к удалению фестиваля имеют только пользователи с правами администратора.

    Атрибуты:
        model (models.Model): Модель фестиваля для удаления.
        context_object_name (str): Имя объекта контекста для шаблона.
    """

    model = models.Festival
    context_object_name = 'festival'

    def has_permission(self):
        """
        Проверяет, имеет ли пользователь права на удаление фестиваля.

        Параметры:
            None

        Возвращает:
            bool: True, если пользователь является суперпользователем, иначе False.
        """
        return self.request.user.is_superuser

    def get_success_url(self):
        """
        Возвращает URL для перенаправления после успешного удаления фестиваля.

        Параметры:
            None

        Возвращает:
            str: URL для перенаправления после удаления.
        """
        return reverse('festivals')


class FestivalRequests(generic.ListView):
    """
    View для отображения запросов на участие в фестивале.

    Этот класс отображает список запросов на участие в фестивале, которые еще не были одобрены.

    Атрибуты:
        model (models.Model): Модель запроса на участие в фестивале для отображения.
        context_object_name (str): Имя объекта контекста для шаблона.
        template_name (str): Путь к шаблону страницы со списком запросов.
        paginate_by (int): Количество запросов на одной странице.
    """

    model = models.FestivalParticipationRequest
    context_object_name = 'requests'
    template_name = 'festivals/request_list.html'
    paginate_by = 50

    def get_queryset(self):
        """
        Возвращает список запросов на участие в фестивале, которые еще не были одобрены.

        Параметры:
            None

        Возвращает:
            QuerySet: Список запросов, не одобренных на участие в фестивале.
        """
        festival_id = self.kwargs.get('pk')
        self.festival = models.Festival.objects.get(pk=festival_id)
        return self.festival.requests.exclude(approved=True).order_by('-created_at')

    def get_context_data(self, **kwargs):
        """
        Добавляет дополнительный контекст на страницу со списком запросов на участие в фестивале.

        Добавляет в контекст фестиваль и заголовок страницы.

        Параметры:
            **kwargs: Дополнительные аргументы для контекста.

        Возвращает:
            dict: Контекст для рендеринга шаблона, включая фестиваль и заголовок страницы.
        """
        context = super().get_context_data(**kwargs)
        context['festival'] = self.festival
        context['page_title'] = f'{self.festival} - Запросы на фестиваль'
        context['user'] = self.request.user
        return context


class FestivalApprovedClubs(generic.ListView):
    """
    View для отображения одобренных клубов на фестивале.

    Этот класс отображает список одобренных клубов на фестивале.

    Атрибуты:
        model (models.Model): Модель запроса на участие в фестивале для отображения.
        context_object_name (str): Имя объекта контекста для шаблона.
        template_name (str): Путь к шаблону страницы со списком одобренных клубов.
        paginate_by (int): Количество клубов на одной странице.
    """

    model = models.FestivalParticipationRequest
    context_object_name = 'requests'
    template_name = 'festivals/approved_clubs.html'
    paginate_by = 50

    def get_queryset(self):
        """
        Возвращает список одобренных клубов на фестивале.

        Параметры:
            None

        Возвращает:
            QuerySet: Список одобренных клубов на фестивале.
        """
        festival_id = self.kwargs.get('pk')
        self.festival = models.Festival.objects.get(pk=festival_id)
        return self.festival.requests.filter(approved=True).order_by('-created_at')

    def get_context_data(self, **kwargs):
        """
        Добавляет дополнительный контекст на страницу со списком одобренных клубов на фестивале.

        Добавляет в контекст фестиваль и заголовок страницы.

        Параметры:
            **kwargs: Дополнительные аргументы для контекста.

        Возвращает:
            dict: Контекст для рендеринга шаблона, включая фестиваль и заголовок страницы.
        """
        context = super().get_context_data(**kwargs)
        context['festival'] = self.festival
        context['page_title'] = f'{self.festival} - Участники фестиваля'
        context['user'] = self.request.user
        return context
