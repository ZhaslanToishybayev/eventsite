from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Case, When, Value, BooleanField
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.views import generic

from clubs import models, forms
from clubs.mixins import ClubRelatedObjectCreateMixin


class ClubEventListView(generic.ListView):
    """
    View для отображения списка событий клубов.

    Этот класс отображает список всех событий клубов с пагинацией. События сортируются по времени, с пометкой на прошедшие.

    Атрибуты:
        model (models.Model): Модель события клуба для отображения.
        context_object_name (str): Имя объекта контекста для шаблона.
        template_name (str): Путь к шаблону страницы со списком событий.
        paginate_by (int): Количество событий на одной странице.
    """

    model = models.ClubEvent
    context_object_name = 'events'
    template_name = 'clubs/club_events.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        """
        Добавляет дополнительный контекст на страницу со списком событий клубов.

        Добавляет в контекст заголовок страницы.

        Параметры:
            **kwargs: Дополнительные аргументы для контекста.

        Возвращает:
            dict: Контекст для рендеринга шаблона, включая заголовок страницы.
        """
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'События клубов'
        return ctx

    def get_queryset(self):
        """
        Возвращает отсортированный список событий клубов.

        События сортируются по времени, с пометкой на прошедшие.

        Параметры:
            None

        Возвращает:
            QuerySet: Список событий клубов с аннотацией на прошедшие события.
        """
        qs = models.ClubEvent.objects.annotate(
            datetime_passed=Case(
                When(start_datetime__lt=timezone.now(), then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            )
        ).order_by('datetime_passed', 'start_datetime')
        return qs


class UpdateEventView(PermissionRequiredMixin, generic.UpdateView):
    model = models.ClubEvent
    form_class = forms.CreateClubEventForm
    template_name = 'clubs/update_event.html'

    def has_permission(self):
        """
        Проверяет, имеет ли текущий пользователь разрешение редактирование события клуба.

        Параметры:
            None

        Возвращает:
            bool: True, если пользователь является менеджером клуба, иначе False.
        """
        return self.request.user in self.get_object().club.managers.all()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Редактировать событие'
        ctx['service'] = self.object
        return ctx

    def form_valid(self, form):
        if form.is_valid():
            event = form.save(commit=False)
            event.save()
            return HttpResponseRedirect(reverse('event_detail', kwargs={'pk': self.get_object().pk}))
        else:
            return super().form_invalid(form)


class EventDetailView(generic.DetailView):
    """
    View для отображения подробностей события клуба.

    Этот класс отображает страницу с подробностями выбранного события клуба.

    Атрибуты:
        model (models.Model): Модель события клуба для отображения.
        context_object_name (str): Имя объекта контекста для шаблона.
        template_name (str): Путь к шаблону страницы с деталями события.
    """

    model = models.ClubEvent
    context_object_name = 'event'
    template_name = 'clubs/event_detail.html'

    def get_context_data(self, **kwargs):
        """
        Добавляет дополнительный контекст на страницу с деталями события.

        Добавляет в контекст название события.

        Параметры:
            **kwargs: Дополнительные аргументы для контекста.

        Возвращает:
            dict: Контекст для рендеринга шаблона, включая название события.
        """
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = self.get_object().title
        return ctx


class CreateClubEventView(ClubRelatedObjectCreateMixin, PermissionRequiredMixin, generic.CreateView):
    """
    View для создания нового события клуба.

    Этот класс обрабатывает создание нового события для клуба. Доступ к созданию события имеют только авторизованные пользователи,
    имеющие соответствующие права доступа.

    Атрибуты:
        model (models.Model): Модель события клуба для создания.
        form_class (forms.Form): Форма для создания события клуба.
        template_name (str): Путь к шаблону страницы создания события.
    """

    model = models.ClubEvent
    form_class = forms.CreateClubEventForm
    template_name = 'clubs/create_event.html'

    def get_context_data(self, **kwargs):
        """
        Добавляет дополнительный контекст на страницу создания события клуба.

        Добавляет в контекст заголовок страницы с указанием клуба, для которого создается событие.

        Параметры:
            **kwargs: Дополнительные аргументы для контекста.

        Возвращает:
            dict: Контекст для рендеринга шаблона, включая заголовок страницы.
        """
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f'Организация события от клуба - {self.get_club()}'
        return ctx
