from django.urls import reverse
from django.views.generic import CreateView, UpdateView, DetailView, ListView, DeleteView

from clubs.forms import PublicationForm
from clubs.models import Publication


class PublicationCreateView(CreateView):
    """
    View для создания новой публикации.

    Этот класс отображает форму для создания новой публикации и обрабатывает её отправку.

    Атрибуты:
        model (models.Model): Модель публикации.
        form_class (forms.Form): Форма для создания публикации.
        template_name (str): Путь к шаблону страницы создания публикации.

    Методы:
        get_context_data(**kwargs):
            Добавляет заголовок страницы в контекст.

        get_success_url():
            Определяет URL для перенаправления после успешного создания публикации.
    """

    model = Publication
    form_class = PublicationForm
    template_name = 'clubs/publication_create.html'

    def get_context_data(self, **kwargs):
        """
        Добавляет заголовок страницы в контекст.

        Параметры:
            **kwargs: Дополнительные аргументы для контекста.

        Возвращает:
            dict: Обновленный контекст для рендеринга шаблона создания публикации.
        """
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Добавить пост'
        return ctx

    def get_success_url(self):
        """
        Определяет URL для перенаправления после успешного создания публикации.

        Возвращает:
            str: URL для перенаправления.
        """
        return reverse('publications')


class PublicationDetailView(DetailView):
    """
    View для отображения деталей публикации.

    Этот класс отображает подробную информацию о конкретной публикации.

    Атрибуты:
        model (models.Model): Модель публикации.
        template_name (str): Путь к шаблону страницы с деталями публикации.
        context_object_name (str): Имя объекта контекста для шаблона.

    Методы:
        get_context_data(**kwargs):
            Добавляет заголовок страницы в контекст.
    """

    model = Publication
    template_name = 'clubs/publication_detail.html'
    context_object_name = 'publication'

    def get_context_data(self, **kwargs):
        """
        Добавляет заголовок страницы в контекст.

        Параметры:
            **kwargs: Дополнительные аргументы для контекста.

        Возвращает:
            dict: Обновленный контекст для рендеринга шаблона с деталями публикации.
        """
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f'Пост - {self.object.title}'
        return ctx


class PublicationListView(ListView):
    """
    View для отображения списка публикаций.

    Этот класс отображает список всех публикаций с возможностью постраничного разбиения.

    Атрибуты:
        model (models.Model): Модель публикации.
        template_name (str): Путь к шаблону страницы со списком публикаций.
        context_object_name (str): Имя объекта контекста для шаблона.
        paginate_by (int): Количество публикаций на одной странице.

    Методы:
        get_context_data(**kwargs):
            Добавляет заголовок страницы в контекст.
    """

    model = Publication
    template_name = 'clubs/publication_list.html'
    context_object_name = 'publications'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        """
        Добавляет заголовок страницы в контекст.

        Параметры:
            **kwargs: Дополнительные аргументы для контекста.

        Возвращает:
            dict: Обновленный контекст для рендеринга шаблона со списком публикаций.
        """
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Публикации'
        return ctx


class PublicationUpdateView(UpdateView):
    """
    View для обновления существующей публикации.

    Этот класс отображает форму для редактирования публикации и обрабатывает её отправку.

    Атрибуты:
        model (models.Model): Модель публикации.
        form_class (forms.Form): Форма для редактирования публикации.
        template_name (str): Путь к шаблону страницы редактирования публикации.

    Методы:
        get_context_data(**kwargs):
            Добавляет заголовок страницы в контекст.

        get_success_url():
            Определяет URL для перенаправления после успешного обновления публикации.
    """

    model = Publication
    form_class = PublicationForm
    template_name = 'clubs/publication_create.html'

    def get_context_data(self, **kwargs):
        """
        Добавляет заголовок страницы в контекст.

        Параметры:
            **kwargs: Дополнительные аргументы для контекста.

        Возвращает:
            dict: Обновленный контекст для рендеринга шаблона редактирования публикации.
        """
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f'Изменение поста - {self.object.title}'
        return ctx

    def get_success_url(self):
        """
        Определяет URL для перенаправления после успешного обновления публикации.

        Возвращает:
            str: URL для перенаправления.
        """
        return self.object.get_absolute_url()


class PublicationDeleteView(DeleteView):
    """
    View для удаления публикации.

    Этот класс отображает страницу подтверждения удаления публикации и обрабатывает её удаление.

    Атрибуты:
        model (models.Model): Модель публикации.
        template_name (str): Путь к шаблону страницы подтверждения удаления публикации.

    Методы:
        has_permission():
            Проверяет, имеет ли текущий пользователь права для удаления публикации.

        get_success_url():
            Определяет URL для перенаправления после успешного удаления публикации.

        get_context_data(**kwargs):
            Добавляет дополнительную информацию о публикации в контекст.
    """

    model = Publication
    template_name = 'clubs/object_delete_confirm.html'

    def has_permission(self):
        """
        Проверяет, имеет ли текущий пользователь права для удаления публикации.

        Возвращает:
            bool: True, если пользователь является суперпользователем; иначе False.
        """
        return self.request.user.is_superuser

    def get_success_url(self):
        """
        Определяет URL для перенаправления после успешного удаления публикации.

        Возвращает:
            str: URL для перенаправления.
        """
        return reverse('publications')

    def get_context_data(self, **kwargs):
        """
        Добавляет дополнительную информацию о публикации в контекст.

        Параметры:
            **kwargs: Дополнительные аргументы для контекста.

        Возвращает:
            dict: Обновленный контекст для рендеринга шаблона подтверждения удаления публикации.
        """
        context = super().get_context_data(**kwargs)
        context['object_name'] = f'публикацию - "{self.object.title}"'
        context['object_id'] = self.object.pk
        context['action_url'] = 'publication_delete'
        return context
