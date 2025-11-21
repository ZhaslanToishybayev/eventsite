from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.views import generic
from clubs.forms import ServiceForClubCreateForm
from clubs.models import ServiceForClubs


class ServiceForClubsCreateView(PermissionRequiredMixin, generic.CreateView):
    """
    View для создания новой услуги для сообществ.

    Этот класс отображает форму для создания новой услуги и обрабатывает её отправку.

    Атрибуты:
        template_name (str): Путь к шаблону страницы создания услуги.
        form_class (forms.Form): Форма для создания услуги.

    Методы:
        has_permission():
            Проверяет, имеет ли текущий пользователь права для создания услуги.

        get_context_data(**kwargs):
            Добавляет заголовок страницы в контекст.

        form_valid(form):
            Обрабатывает форму после её успешной проверки.
    """

    template_name = 'clubs/create_service_for_clubs.html'
    form_class = ServiceForClubCreateForm

    def has_permission(self):
        """
        Проверяет, имеет ли текущий пользователь права для создания услуги.

        Возвращает:
            bool: True, если пользователь является суперпользователем; иначе False.
        """
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        """
        Добавляет заголовок страницы в контекст.

        Параметры:
            **kwargs: Дополнительные аргументы для контекста.

        Возвращает:
            dict: Обновленный контекст для рендеринга шаблона создания услуги.
        """
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Добавить услугу для сообществ'
        return ctx

    def form_valid(self, form):
        """
        Обрабатывает форму после её успешной проверки.

        Параметры:
            form (forms.Form): Успешно проверенная форма.

        Возвращает:
            HttpResponseRedirect: Перенаправление на страницу услуги после успешного создания.
        """
        if form.is_valid():
            service = form.save(commit=True)
            return redirect(service.get_absolute_url())
        else:
            return self.form_invalid(form)


class ServiceForClubDetailView(generic.DetailView):
    """
    View для отображения деталей услуги для сообществ.

    Этот класс отображает подробную информацию о конкретной услуге.

    Атрибуты:
        model (models.Model): Модель услуги для сообществ.
        template_name (str): Путь к шаблону страницы с деталями услуги.
        context_object_name (str): Имя объекта контекста для шаблона.

    Методы:
        get_context_data(**kwargs):
            Добавляет заголовок страницы в контекст.
    """

    model = ServiceForClubs
    template_name = 'clubs/service_for_club_detail.html'
    context_object_name = 'service_for_club'

    def get_context_data(self, **kwargs):
        """
        Добавляет заголовок страницы в контекст.

        Параметры:
            **kwargs: Дополнительные аргументы для контекста.

        Возвращает:
            dict: Обновленный контекст для рендеринга шаблона с деталями услуги.
        """
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f'Услуга для сообществ - {self.object.name}'
        return ctx


class ServiceForClubsEditView(PermissionRequiredMixin, generic.UpdateView):
    """
    View для редактирования существующей услуги для сообществ.

    Этот класс отображает форму для редактирования услуги и обрабатывает её отправку.

    Атрибуты:
        template_name (str): Путь к шаблону страницы редактирования услуги.
        form_class (forms.Form): Форма для редактирования услуги.
        model (models.Model): Модель услуги для сообществ.

    Методы:
        has_permission():
            Проверяет, имеет ли текущий пользователь права для редактирования услуги.

        get_context_data(**kwargs):
            Добавляет заголовок страницы в контекст.
    """

    template_name = 'clubs/create_service_for_clubs.html'
    form_class = ServiceForClubCreateForm
    model = ServiceForClubs

    def has_permission(self):
        """
        Проверяет, имеет ли текущий пользователь права для редактирования услуги.

        Возвращает:
            bool: True, если пользователь является суперпользователем; иначе False.
        """
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        """
        Добавляет заголовок страницы в контекст.

        Параметры:
            **kwargs: Дополнительные аргументы для контекста.

        Возвращает:
            dict: Обновленный контекст для рендеринга шаблона редактирования услуги.
        """
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f'Редактировать услугу - {self.object.name}'
        return ctx


class ServiceForClubsListView(generic.ListView):
    """
    View для отображения списка всех услуг для сообществ.

    Этот класс отображает список всех услуг с возможностью постраничного разбиения.

    Атрибуты:
        model (models.Model): Модель услуги для сообществ.
        template_name (str): Путь к шаблону страницы со списком услуг.
        context_object_name (str): Имя объекта контекста для шаблона.

    Методы:
        get_context_data(**kwargs):
            Добавляет заголовок страницы в контекст.
    """

    model = ServiceForClubs
    template_name = 'clubs/service_for_clubs_list.html'
    context_object_name = 'services'

    def get_context_data(self, **kwargs):
        """
        Добавляет заголовок страницы в контекст.

        Параметры:
            **kwargs: Дополнительные аргументы для контекста.

        Возвращает:
            dict: Обновленный контекст для рендеринга шаблона со списком услуг.
        """
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Все услуги для сообществ'
        return ctx


class ServiceForClubsDeleteView(PermissionRequiredMixin, generic.DeleteView):
    """
    View для удаления услуги для сообществ.

    Этот класс отображает страницу подтверждения удаления услуги и обрабатывает её удаление.

    Атрибуты:
        model (models.Model): Модель услуги для сообществ.
        template_name (str): Путь к шаблону страницы подтверждения удаления услуги.

    Методы:
        has_permission():
            Проверяет, имеет ли текущий пользователь права для удаления услуги.

        get_success_url():
            Определяет URL для перенаправления после успешного удаления услуги.

        get_context_data(**kwargs):
            Добавляет дополнительную информацию о услуге в контекст.
    """

    model = ServiceForClubs
    template_name = 'clubs/object_delete_confirm.html'

    def has_permission(self):
        """
        Проверяет, имеет ли текущий пользователь права для удаления услуги.

        Возвращает:
            bool: True, если пользователь является суперпользователем; иначе False.
        """
        return self.request.user.is_superuser

    def get_success_url(self):
        """
        Определяет URL для перенаправления после успешного удаления услуги.

        Возвращает:
            str: URL для перенаправления.
        """
        return reverse('service_for_club_list')

    def get_context_data(self, **kwargs):
        """
        Добавляет дополнительную информацию о услуге в контекст.

        Параметры:
            **kwargs: Дополнительные аргументы для контекста.

        Возвращает:
            dict: Обновленный контекст для рендеринга шаблона подтверждения удаления услуги.
        """
        context = super().get_context_data(**kwargs)
        context['object_name'] = f'услугу - "{self.object.name}"'
        context['object_id'] = self.object.pk
        context['action_url'] = 'service_for_club_delete'
        return context
