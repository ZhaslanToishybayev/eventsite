from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView, PasswordResetView as _PasswordResetView
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Q
from django.shortcuts import redirect, render
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.views.generic.edit import FormMixin
from django.views.generic.base import TemplateView

from .forms import RegisterUserForm, UserLoginForm, UserUpdateForm, PasswordResetForm
from .models import User, phone_regex_validator
from django.urls import reverse_lazy


class PasswordResetView(_PasswordResetView):
    email_template_name = "registration/password_reset_email.html"
    extra_email_context = None
    form_class = PasswordResetForm
    from_email = None
    html_email_template_name = None
    subject_template_name = "registration/password_reset_subject.txt"
    success_url = reverse_lazy("password_reset_done")
    template_name = "registration/password_reset_form.html"
    title = _("Password reset")
    token_generator = default_token_generator

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    # def form_valid(self, form):
    #     opts = {
    #         "use_https": self.request.is_secure(),
    #         "token_generator": self.token_generator,
    #         "from_email": self.from_email,
    #         "email_template_name": self.email_template_name,
    #         "subject_template_name": self.subject_template_name,
    #         "request": self.request,
    #         "html_email_template_name": self.html_email_template_name,
    #         "extra_email_context": self.extra_email_context,
    #     }
    #     form.save(**opts)
    #     return super().form_valid(form)


class RegisterUserView(generic.FormView):
    """
    View для регистрации нового пользователя.

    Этот класс обрабатывает форму регистрации нового пользователя. Если пользователь уже аутентифицирован,
    его перенаправляют на главную страницу. Если форма успешно валидируется, новый пользователь создается и
    аутентифицируется, после чего происходит перенаправление на страницу, с которой пришел пользователь.
    """

    form_class = RegisterUserForm
    template_name = 'accounts/register_user.html'

    def get_context_data(self, **kwargs):
        """
        Добавляет дополнительный контекст в шаблон.

        Параметры:
            **kwargs: Дополнительные аргументы для контекста.

        Возвращает:
            dict: Контекст для рендеринга шаблона.
        """
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Центр сообществ - Регистрация'
        return ctx

    def get(self, request, *args, **kwargs):
        """
        Обрабатывает GET-запрос для регистрации пользователя.

        Перенаправляет аутентифицированных пользователей на главную страницу. Если пользователь не аутентифицирован,
        вызывает родительский метод для рендеринга страницы регистрации.

        Параметры:
            request (HttpRequest): Объект запроса.

        Возвращает:
            HttpResponseRedirect или HttpResponse: Результат обработки запроса.
        """
        if self.request.user.is_authenticated:
            return redirect('index')
        else:
            return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Обрабатывает валидную форму регистрации.

        Если форма валидна, сохраняет нового пользователя, аутентифицирует его и перенаправляет на страницу
        успешного завершения регистрации.

        Параметры:
            form (RegisterUserForm): Валидная форма регистрации.

        Возвращает:
            HttpResponseRedirect: Перенаправление на URL, указанный в get_success_url.
        """
        if form.is_valid():
            user = form.save()
            login(self.request, user)
            return redirect(self.get_success_url())
        else:
            return super().form_invalid(form)

    def get_success_url(self):
        """
        Определяет URL для перенаправления после успешной регистрации.

        Возвращает URL, с которого пришел пользователь (HTTP_REFERER), или корневой URL ('/').

        Возвращает:
            str: URL для перенаправления.
        """
        success_url = self.request.META.get('HTTP_REFERER', '/')
        return success_url


class LoginUserView(LoginView):
    """
    View для страницы входа пользователя.

    Этот класс обрабатывает страницу входа в систему, используя форму для входа пользователя.

    Атрибуты:
        form_class (forms.Form): Форма для входа пользователя.
        template_name (str): Путь к шаблону страницы входа.
    """

    form_class = UserLoginForm
    template_name = 'accounts/login_user.html'


class UserDetailView(generic.DetailView):
    """
    View для отображения деталей пользователя.

    Этот класс обрабатывает отображение страницы с деталями пользователя. Если профиль пользователя
    скрыт, вызывается исключение PermissionDenied. В противном случае, отображается страница с деталями пользователя.

    Атрибуты:
        model (models.Model): Модель пользователя для отображения.
        context_object_name (str): Имя объекта контекста для шаблона.
        template_name (str): Путь к шаблону страницы с деталями пользователя.
    """

    model = User
    context_object_name = 'user'
    template_name = 'accounts/user_detail.html'

    def get_context_data(self, **kwargs):
        """
        Добавляет дополнительный контекст в шаблон.

        Параметры:
            **kwargs: Дополнительные аргументы для контекста.

        Возвращает:
            dict: Контекст для рендеринга шаблона, включая название страницы.
        """
        ctx = super().get_context_data(**kwargs)
        user = ctx['user']  # Используем уже загруженный объект из get_queryset
        ctx['page_title'] = user
        return ctx

    def get_queryset(self):
        """
        Возвращает оптимизированный queryset для пользователя.

        Оптимизирует запросы для избежания N+1 проблем с клубами пользователя.

        Возвращает:
            QuerySet: Оптимизированный queryset пользователя.
        """
        return super().get_queryset().prefetch_related(
            'members_of_clubs__category',
            'members_of_clubs__city',
            'managed_clubs__category',
            'managed_clubs__city'
        )

    def get(self, request, *args, **kwargs):
        """
        Обрабатывает GET-запрос для отображения деталей пользователя.

        Если профиль пользователя закрыт для отображения, возбуждается исключение PermissionDenied.
        В противном случае, вызывается родительский метод для рендеринга страницы.

        Параметры:
            request (HttpRequest): Объект запроса.
            *args: Дополнительные аргументы.
            **kwargs: Дополнительные именованные аргументы.

        Возвращает:
            HttpResponse: Результат обработки запроса.

        Исключения:
            PermissionDenied: Если профиль пользователя закрыт для отображения.
        """
        user = self.get_object()
        # Allow access if the profile is displayed in allies OR if the requesting user IS the profile owner
        if user.is_displayed_in_allies or (request.user.is_authenticated and request.user == user):
            return super().get(request, *args, **kwargs)
        else:
            raise PermissionDenied("Профиль пользователя закрыт")


class UserListView(generic.ListView):
    """
    View для отображения списка пользователей.

    Этот класс обрабатывает отображение списка пользователей с возможностью поиска и пагинации. Пользователи,
    которые не должны отображаться (определяется полем is_displayed_in_allies), исключаются из результатов.
    Также исключается текущий аутентифицированный пользователь из списка.

    Атрибуты:
        model (models.Model): Модель пользователя для отображения.
        context_object_name (str): Имя объекта контекста для шаблона.
        template_name (str): Путь к шаблону страницы со списком пользователей.
        paginate_by (int): Количество пользователей на одной странице.
        ordering (list): Список полей для сортировки пользователей.
    """

    model = User
    context_object_name = 'users'
    template_name = 'accounts/user_list.html'
    paginate_by = 10
    ordering = ['first_name', 'last_name']

    def get_queryset(self):
        """
        Возвращает отфильтрованный и отсортированный queryset пользователей.

        Фильтрация осуществляется по полю is_displayed_in_allies и по параметрам поиска из GET-запроса.
        Параметры поиска включают поиск по всем полям, интересам или имени. Также исключается текущий аутентифицированный пользователь.

        Параметры:
            None

        Возвращает:
            QuerySet: Отфильтрованный и отсортированный список пользователей.
        """
        qs = super().get_queryset().filter(is_displayed_in_allies=True)
        search_query = self.request.GET.get('search')
        search_field = self.request.GET.get('search-field')

        if search_query:
            if search_field == 'all':
                qs = User.objects.filter(
                    Q(profile__about__icontains=search_query) |
                    Q(profile__goals_for_life__icontains=search_query) |
                    Q(profile__interests__icontains=search_query) |
                    Q(first_name__icontains=search_query) |
                    Q(last_name__icontains=search_query)
                )
            elif search_field == 'interests':
                qs = User.objects.filter(
                    Q(profile__about__icontains=search_query) |
                    Q(profile__goals_for_life__icontains=search_query) |
                    Q(profile__interests__icontains=search_query)
                )
            elif search_field == 'name':
                qs = User.objects.filter(
                    Q(first_name__icontains=search_query) |
                    Q(last_name__icontains=search_query)
                )
            return qs.exclude(id=self.request.user.id)

        return User.objects.filter(is_displayed_in_allies=True).exclude(id=self.request.user.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search')
        context['search_field'] = self.request.GET.get('search-field')
        return context


class UserUpdateView(LoginRequiredMixin, generic.FormView):
    """
    View для обновления профиля пользователя.

    Этот класс обрабатывает страницу для обновления профиля текущего аутентифицированного пользователя.
    При GET-запросе отображает форму с текущими данными пользователя. При POST-запросе обновляет данные пользователя
    и перенаправляет его на страницу с обновленным профилем.

    Атрибуты:
        form_class (forms.Form): Форма для обновления профиля пользователя.
        template_name (str): Путь к шаблону страницы обновления профиля.
    """

    form_class = UserUpdateForm
    template_name = 'accounts/update_profile.html'

    def get(self, request, *args, **kwargs):
        """
        Обрабатывает GET-запрос для отображения формы обновления профиля.

        Создает форму с текущими данными пользователя и добавляет её в контекст шаблона. Устанавливает заголовок страницы.

        Параметры:
            request (HttpRequest): Объект запроса.
            *args: Дополнительные аргументы.
            **kwargs: Дополнительные именованные аргументы.

        Возвращает:
            HttpResponse: Ответ с рендерингом шаблона формы обновления профиля.
        """
        form = self.form_class(instance=request.user)
        page_title = 'Изменить профиль'
        ctx = {
            'page_title': page_title,
            'form': form,
        }
        return self.render_to_response(ctx)

    def post(self, request, *args, **kwargs):
        """
        Обрабатывает POST-запрос для обновления данных профиля пользователя.

        При успешной валидации формы обновляет данные пользователя и перенаправляет его на страницу профиля.
        Если форма невалидна, возвращает ту же страницу с ошибками формы.

        Параметры:
            request (HttpRequest): Объект запроса.
            *args: Дополнительные аргументы.
            **kwargs: Дополнительные именованные аргументы.

        Возвращает:
            HttpResponse: Перенаправление на страницу профиля при успешной валидации формы, или рендеринг той же страницы с ошибками формы.
        """
        form = self.form_class(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save()
            return redirect(user.get_absolute_url())
        else:
            return self.render_to_response({'form': form})


@login_required
def find_allies_view(request):
    """
    View для страницы "Единомышленники" - поиска и фильтрации пользователей.

    Позволяет искать пользователей по:
    - Интересам
    - Городу
    - Возрасту
    - Имени

    Параметры:
        request (HttpRequest): Объект запроса

    Возвращает:
        HttpResponse: Страницу с результатами поиска
    """
    # Начинаем с пользователей, которые отображаются в списке
    users = User.objects.filter(is_displayed_in_allies=True).exclude(id=request.user.id)

    # Параметры поиска из GET запроса
    search_query = request.GET.get('search', '').strip()
    search_field = request.GET.get('search_field', 'all')
    city_filter = request.GET.get('city', '').strip()
    min_age = request.GET.get('min_age', '').strip()
    max_age = request.GET.get('max_age', '').strip()
    gender_filter = request.GET.get('gender', '').strip()

    # Поиск по интересам и другим полям профиля
    if search_query:
        if search_field == 'interests':
            users = users.filter(
                Q(profile__interests__icontains=search_query) |
                Q(profile__about__icontains=search_query) |
                Q(profile__goals_for_life__icontains=search_query)
            )
        elif search_field == 'city':
            users = users.filter(profile__city__icontains=search_query)
        elif search_field == 'name':
            users = users.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query)
            )
        else:  # all fields
            users = users.filter(
                Q(profile__interests__icontains=search_query) |
                Q(profile__about__icontains=search_query) |
                Q(profile__goals_for_life__icontains=search_query) |
                Q(profile__city__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query)
            )

    # Фильтрация по городу
    if city_filter:
        users = users.filter(profile__city__icontains=city_filter)

    # Фильтрация по возрасту (если есть поле age в Profile)
    # Пока пропустим, так как в модели Profile нет поля age

    # Фильтрация по полу (если есть поле gender в Profile)
    # Пока пропустим, так как в модели Profile нет поля gender

    # Сортировка
    users = users.order_by('first_name', 'last_name')

    # Пагинация
    from django.core.paginator import Paginator

    paginator = Paginator(users, 12)  # 12 пользователей на странице
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'search_field': search_field,
        'city_filter': city_filter,
        'min_age': min_age,
        'max_age': max_age,
        'gender_filter': gender_filter,
        'page_title': 'Единомышленники',
    }

    return render(request, 'accounts/find_allies.html', context)


@login_required
def set_phone_view(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')

        # Basic validation
        if not phone:
            messages.error(request, "Пожалуйста, введите номер телефона.")
            return render(request, 'accounts/set_phone.html')

        # Check if phone is already taken
        if User.objects.filter(phone=phone).exclude(pk=request.user.pk).exists():
            messages.error(request, "Этот номер телефона уже используется другим пользователем.")
            return render(request, 'accounts/set_phone.html')

        try:
            # Validate format
            phone_regex_validator(phone)

            # Save
            request.user.phone = phone
            request.user.save()

            messages.success(request, "Номер телефона успешно сохранен!")
            return redirect('index') # Or wherever you want them to go

        except ValidationError as e:
            messages.error(request, e.message)
            return render(request, 'accounts/set_phone.html')

    return render(request, 'accounts/set_phone.html')
