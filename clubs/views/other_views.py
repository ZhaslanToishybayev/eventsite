from django.views import generic

from clubs import models

class IndexView(generic.TemplateView):
    """
    View для отображения главной страницы сайта.

    Этот класс отображает главную страницу, включая топ-16 клубов, ближайшие 16 событий и 3 услуги для клубов.

    Атрибуты:
        template_name (str): Путь к шаблону главной страницы.
    """

    template_name = 'clubs/index.html'

    def get_context_data(self, **kwargs):
        """
        Добавляет дополнительный контекст на главную страницу.

        В контекст добавляются:
        - Топ-16 клубов, отсортированных по количеству участников и лайков.
        - Ближайшие 16 событий, отсортированных по дате начала.
        - 3 услуги для клубов, отсортированных по дате создания.

        Параметры:
            **kwargs: Дополнительные аргументы для контекста.

        Возвращает:
            dict: Контекст для рендеринга шаблона главной страницы.
        """
        context = super().get_context_data(**kwargs)
        context['top_16_clubs'] = models.Club.objects.all().order_by('-members_count', '-likes_count')[:16]
        context['nearest_16_events'] = models.ClubEvent.objects.all().order_by('start_datetime')[:16]
        context['services'] = models.ServiceForClubs.objects.all().order_by('created_at')
        return context


class EventCalendarView(generic.ListView):
    """
    View для отображения календаря событий клубов.

    Этот класс отображает список всех событий клубов. События можно фильтровать и сортировать по необходимости в будущем.

    Атрибуты:
        model (models.Model): Модель события клуба для отображения.
        context_object_name (str): Имя объекта контекста для шаблона.
        template_name (str): Путь к шаблону страницы с календарем событий.
    """

    model = models.ClubEvent
    context_object_name = 'events'
    template_name = 'clubs/event_calendar.html'


class AboutView(generic.TemplateView):
    """
    View для отображения страницы "О нас".

    Этот класс отображает страницу, содержащую информацию о сайте или организации.

    Атрибуты:
        template_name (str): Путь к шаблону страницы "О нас".
    """

    template_name = 'clubs/about.html'

    def get_context_data(self, **kwargs):
        """
        Добавляет дополнительный контекст на страницу "О нас".

        В контекст добавляется заголовок страницы.

        Параметры:
            **kwargs: Дополнительные аргументы для контекста.

        Возвращает:
            dict: Контекст для рендеринга шаблона страницы "О нас".
        """
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'О НАС'
        return ctx


class PolicyView(generic.TemplateView):
    template_name = 'clubs/policy.html'

    def get_context_data(self, **kwargs):
        """
        Добавляет дополнительный контекст на страницу "О нас".

        В контекст добавляется заголовок страницы.

        Параметры:
            **kwargs: Дополнительные аргументы для контекста.

        Возвращает:
            dict: Контекст для рендеринга шаблона страницы "О нас".
        """
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Публичная оферта'
        return ctx
