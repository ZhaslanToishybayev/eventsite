from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import BooleanField, Case, When, Value
from django.utils import timezone
from clubs import models, forms


class ClubDetailView(generic.DetailView):
    """
    View для отображения деталей клуба.

    Этот класс отображает страницу с деталями выбранного клуба. Также добавляет информацию о предстоящих и прошедших
    событиях клуба в контекст шаблона.

    Атрибуты:
        model (models.Model): Модель клуба для отображения.
        context_object_name (str): Имя объекта контекста для шаблона.
        template_name (str): Путь к шаблону страницы с деталями клуба.
    """

    model = models.Club
    context_object_name = 'club'
    template_name = 'clubs/detail.html'

    def get_context_data(self, **kwargs):
        """
        Добавляет дополнительный контекст на страницу с деталями клуба.

        Добавляет в контекст название страницы и список событий клуба, помечая прошедшие события.
        Оптимизировано для избежания лишних запросов к базе данных.

        Параметры:
            **kwargs: Дополнительные аргументы для контекста.

        Возвращает:
            dict: Контекст для рендеринга шаблона, включая название страницы и список событий клуба.
        """
        context = super().get_context_data(**kwargs)
        club = context['club']  # Используем уже загруженный объект из get_queryset
        context['page_title'] = f'Сообщество - {club.name}'
        context['events'] = models.ClubEvent.objects.annotate(
                                datetime_passed=Case(
                                    When(start_datetime__lt=timezone.now(), then=Value(True)),
                                    default=Value(False),
                                    output_field=BooleanField()
                                )
                            ).filter(club=club).order_by('datetime_passed', 'start_datetime')
        return context

    def get_queryset(self):
        """
        Возвращает отфильтрованный и оптимизированный список клубов.

        Фильтрует клубы, оставляя только активные, и оптимизирует запросы для избежания N+1 проблем.

        Параметры:
            None

        Возвращает:
            QuerySet: Список активных клубов с оптимизированными связями.
        """
        return super().get_queryset().filter(is_active=True).select_related(
            'category',
            'city',
            'creater'
        ).prefetch_related(
            'gallery_photos',
            'services__images',
            'posts',
            'managers',
            'members',
            'partners',
            'likes'
        )


class ClubListView(generic.ListView):
    """
    View для отображения списка клубов.

    Этот класс обрабатывает отображение списка всех активных клубов с возможностью поиска. Клубы пагинируются по 40 на странице.

    Атрибуты:
        model (models.Model): Модель клуба для отображения.
        context_object_name (str): Имя объекта контекста для шаблона.
        template_name (str): Путь к шаблону страницы со списком клубов.
        paginate_by (int): Количество клубов на одной странице.
    """

    model = models.Club
    context_object_name = 'clubs'
    template_name = 'clubs/clubs.html'
    paginate_by = 40

    def get_context_data(self, **kwargs):
        """
        Добавляет дополнительный контекст на страницу со списком клубов.

        Добавляет в контекст заголовок страницы и строку поиска.

        Параметры:
            **kwargs: Дополнительные аргументы для контекста.

        Возвращает:
            dict: Контекст для рендеринга шаблона, включая заголовок страницы и строку поиска.
        """
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'ВСЕ СООБЩЕСТВА'
        context['search'] = self.request.GET.get('search')
        return context

    def get_queryset(self):
        """
        Возвращает отфильтрованный список клубов.

        Фильтрует клубы по строке поиска, если таковая имеется. Оставляет только активные клубы.

        Параметры:
            None

        Возвращает:
            QuerySet: Список активных клубов, соответствующих строке поиска.
        """
        qs = super().get_queryset().filter(is_active=True)
        search_query = self.request.GET.get('search')
        if search_query:
            return qs.filter(name__icontains=search_query)
        return qs


class ClubCreateView(LoginRequiredMixin, PermissionRequiredMixin, generic.CreateView):
    """
    View для создания нового клуба.

    Этот класс обрабатывает форму создания нового клуба. При успешном сохранении клуба, текущий пользователь добавляется
    в качестве создателя, а также в менеджеры и участники клуба.

    Атрибуты:
        model (models.Model): Модель клуба для создания.
        form_class (forms.Form): Форма для создания клуба.
        template_name (str): Путь к шаблону страницы создания клуба.
    """

    model = models.Club
    template_name = 'clubs/create_club.html'
    form_class = forms.ClubForm

    def has_permission(self):
        """
        Проверяет, имеет ли текущий пользователь разрешение на создание клуба.

        Параметры:
            None

        Возвращает:
            bool: True для всех аутентифицированных пользователей.
        """
        # Allow all authenticated users to create clubs
        return True

    def get_context_data(self, **kwargs):
        """
        Добавляет дополнительный контекст на страницу создания клуба.

        Добавляет в контекст заголовок страницы.

        Параметры:
            **kwargs: Дополнительные аргументы для контекста.

        Возвращает:
            dict: Контекст для рендеринга шаблона, включая заголовок страницы.
        """
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Создать сообщество'
        return ctx

    def form_valid(self, form):
        """
        Обрабатывает валидную форму для создания клуба.

        Устанавливает текущего пользователя как создателя клуба и добавляет его в менеджеры и участников клуба.

        Параметры:
            form (forms.Form): Валидная форма создания клуба.

        Возвращает:
            HttpResponse: Перенаправление на страницу клуба после успешного создания.
        """
        if form.is_valid():
            club = form.save(commit=False)
            club.creater = self.request.user
            club.members_count += 1
            club.save()
            club.managers.add(self.request.user)
            club.members.add(self.request.user)
            return redirect(club.get_absolute_url())
        else:
            return super().form_invalid(form)


class ClubEditView(PermissionRequiredMixin, generic.UpdateView):
    """
    View для редактирования существующего клуба.

    Этот класс обрабатывает форму редактирования клуба. Доступ к редактированию клуба имеют только пользователи, которые
    являются менеджерами этого клуба.

    Атрибуты:
        model (models.Model): Модель клуба для редактирования.
        form_class (forms.Form): Форма для редактирования клуба.
        template_name (str): Путь к шаблону страницы редактирования клуба.
    """

    model = models.Club
    template_name = 'clubs/create_club.html'
    form_class = forms.ClubUpdateForm

    def has_permission(self):
        """
        Проверяет, имеет ли текущий пользователь разрешение на редактирование клуба.

        Параметры:
            None

        Возвращает:
            bool: True, если пользователь является менеджером клуба, иначе False.
        """
        return self.request.user in self.get_object().managers.all()


class ClubDeleteView(PermissionRequiredMixin, generic.DeleteView):
    """
    View для удаления клуба.

    Этот класс обрабатывает процесс удаления клуба. Доступ к удалению клуба имеют только пользователи, которые являются
    менеджерами этого клуба. После успешного удаления пользователя перенаправляют на его профиль.

    Атрибуты:
        model (models.Model): Модель клуба для удаления.
        template_name (str): Путь к шаблону страницы подтверждения удаления клуба.
    """

    model = models.Club
    template_name = 'clubs/object_delete_confirm.html'

    def has_permission(self):
        """
        Проверяет, имеет ли текущий пользователь разрешение на удаление клуба.

        Параметры:
            None

        Возвращает:
            bool: True, если пользователь является менеджером клуба, иначе False.
        """
        return self.request.user in self.get_object().managers.all()

    def get_success_url(self):
        """
        Возвращает URL для перенаправления после успешного удаления клуба.

        Параметры:
            None

        Возвращает:
            str: URL профиля пользователя после успешного удаления клуба.
        """
        return self.request.user.get_absolute_url()

    def get_context_data(self, **kwargs):
        """
        Добавляет дополнительный контекст на страницу подтверждения удаления клуба.

        Добавляет в контекст имя и идентификатор объекта, а также URL действия удаления.

        Параметры:
            **kwargs: Дополнительные аргументы для контекста.

        Возвращает:
            dict: Контекст для рендеринга шаблона, включая имя объекта и URL действия удаления.
        """
        context = super().get_context_data(**kwargs)
        context['object_name'] = f'сообщество - "{self.object.name}"'
        context['object_id'] = self.object.pk
        context['action_url'] = 'club_delete'
        return context


class ChooseClubManagersView(PermissionRequiredMixin, generic.UpdateView):
    """
    View для выбора и изменения руководителей клуба.

    Этот класс обрабатывает форму для добавления или удаления руководителей клуба. Доступ к этому представлению имеют
    только пользователи, которые являются менеджерами клуба.

    Атрибуты:
        model (models.Model): Модель клуба для обновления.
        form_class (forms.Form): Форма для выбора руководителей клуба.
        template_name (str): Путь к шаблону страницы выбора руководителей клуба.
    """

    model = models.Club
    template_name = 'clubs/choose_club_managers.html'
    form_class = forms.SelectClubManagersForm

    def has_permission(self):
        """
        Проверяет, имеет ли текущий пользователь разрешение на изменение руководителей клуба.

        Параметры:
            None

        Возвращает:
            bool: True, если пользователь является менеджером клуба, иначе False.
        """
        return self.request.user in self.get_object().managers.all()

    def form_valid(self, form):
        """
        Обрабатывает валидную форму для изменения руководителей клуба.

        Устанавливает новых руководителей клуба и перенаправляет на страницу клуба после успешного обновления.

        Параметры:
            form (forms.Form): Валидная форма для выбора руководителей клуба.

        Возвращает:
            HttpResponse: Перенаправление на страницу клуба после успешного обновления.
        """
        users_after = form.data.getlist('managers')
        check = self.form_class.required_at_least_one_manager
        if form.is_valid() and check(users_after, form):
            self.get_object().managers.set(form.cleaned_data.get('managers'))
            return redirect(self.get_object().get_absolute_url())
        else:
            return render(self.request, self.template_name, context={'form': form})

    def get_context_data(self, **kwargs):
        """
        Добавляет дополнительный контекст на страницу выбора руководителей клуба.

        Добавляет в контекст заголовок страницы.

        Параметры:
            **kwargs: Дополнительные аргументы для контекста.

        Возвращает:
            dict: Контекст для рендеринга шаблона, включая заголовок страницы.
        """
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Добавление/удаление руководителей'
        return ctx

    def get(self, request, *args, **kwargs):
        """
        Обрабатывает GET-запрос для страницы выбора руководителей клуба.

        Инициализирует форму с текущими менеджерами клуба и устанавливает queryset для выбора новых руководителей.

        Параметры:
            request (HttpRequest): Объект запроса.

        Возвращает:
            HttpResponse: Ответ с отрендеренной формой для выбора руководителей.
        """
        form = self.form_class(initial={'managers': self.get_object().managers.all()})
        form.fields['managers'].queryset = self.get_object().members.all().union(self.get_object().managers.all())
        return self.render_to_response({'form': form})
