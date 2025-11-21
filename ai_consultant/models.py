import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class ChatSession(models.Model):
    """
    Модель для хранения сессий чата с ИИ-консультантом
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ai_chat_sessions',
        verbose_name=_('Пользователь'),
        null=True,  # Разрешаем анонимные сессии
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Создана'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Обновлена'))
    is_active = models.BooleanField(default=True, verbose_name=_('Активна'))
    
    # Поля для сохранения состояния агента
    current_agent = models.CharField(
        max_length=50, 
        null=True, 
        blank=True,
        verbose_name=_('Текущий агент'),
        help_text=_('Имя агента, который обрабатывает текущий диалог')
    )
    agent_context = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Контекст агента'),
        help_text=_('Данные для сохранения состояния между сообщениями')
    )

    class Meta:
        verbose_name = _('Сессия чата')
        verbose_name_plural = _('Сессии чата')
        ordering = ['-updated_at']

    def __str__(self):
        user_display = self.user if self.user else 'Анонимный пользователь'
        return f'Чат с {user_display} - {self.created_at.strftime("%d.%m.%Y %H:%M")}'


class ChatMessage(models.Model):
    """
    Модель для хранения сообщений в чате
    """
    ROLE_CHOICES = [
        ('user', _('Пользователь')),
        ('assistant', _('Ассистент')),
        ('system', _('Система')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name=_('Сессия')
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        verbose_name=_('Роль')
    )
    content = models.TextField(verbose_name=_('Содержание'))
    tokens_used = models.PositiveIntegerField(default=0, verbose_name=_('Использовано токенов'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Создано'))

    class Meta:
        verbose_name = _('Сообщение чата')
        verbose_name_plural = _('Сообщения чата')
        ordering = ['created_at']

    def __str__(self):
        return f'{self.role}: {self.content[:50]}...'


class AIContext(models.Model):
    """
    Модель для хранения контекстных данных для ИИ
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=200, unique=True, verbose_name=_('Ключ'))
    content = models.TextField(verbose_name=_('Содержание'))
    category = models.CharField(max_length=100, verbose_name=_('Категория'))
    is_active = models.BooleanField(default=True, verbose_name=_('Активно'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Создано'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Обновлено'))

    class Meta:
        verbose_name = _('Контекст ИИ')
        verbose_name_plural = _('Контексты ИИ')
        ordering = ['category', 'key']

    def __str__(self):
        return f'{self.category}: {self.key}'


class ChatAnalytics(models.Model):
    """
    Модель для аналитики использования чата
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='analytics',
        verbose_name=_('Сессия')
    )
    event_type = models.CharField(max_length=50, verbose_name=_('Тип события'))
    data = models.JSONField(default=dict, verbose_name=_('Данные'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Создано'))

    class Meta:
        verbose_name = _('Аналитика чата')
        verbose_name_plural = _('Аналитика чата')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.event_type} - {self.session}'


class PlatformService(models.Model):
    """
    Модель для хранения информации об услугах платформы
    """
    SERVICE_TYPES = [
        ('rental', 'Аренда оборудования'),
        ('printing', 'Печать и вышивка'),
        ('consultation', 'Консультации специалистов'),
        ('studio', 'Студия интервью'),
        ('merchandise', 'Сувенирная продукция'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, verbose_name=_('Название услуги'))
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES, verbose_name=_('Тип услуги'))
    description = models.TextField(verbose_name=_('Описание'))
    price_info = models.CharField(max_length=500, blank=True, verbose_name=_('Информация о цене'))
    contact_info = models.CharField(max_length=200, blank=True, verbose_name=_('Контактная информация'))
    is_active = models.BooleanField(default=True, verbose_name=_('Активна'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('Порядок отображения'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Создано'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Обновлено'))

    class Meta:
        verbose_name = _('Услуга платформы')
        verbose_name_plural = _('Услуги платформы')
        ordering = ['order', 'title']

    def __str__(self):
        return f'{self.get_service_type_display()}: {self.title}'


class InterviewRequest(models.Model):
    """
    Модель для заявок на интервью
    """
    STATUS_CHOICES = [
        ('pending', 'Ожидает рассмотрения'),
        ('approved', 'Одобрена'),
        ('scheduled', 'Запланирована'),
        ('completed', 'Завершена'),
        ('cancelled', 'Отменена'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='interview_requests',
        verbose_name=_('Пользователь')
    )
    project_name = models.CharField(max_length=200, verbose_name=_('Название проекта'))
    project_description = models.TextField(verbose_name=_('Описание проекта'))
    preferred_dates = models.CharField(max_length=200, verbose_name=_('Предпочтительные даты'))
    contact_info = models.CharField(max_length=200, verbose_name=_('Контактная информация'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_('Статус'))
    notes = models.TextField(blank=True, verbose_name=_('Заметки'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Создано'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Обновлено'))

    class Meta:
        verbose_name = _('Заявка на интервью')
        verbose_name_plural = _('Заявки на интервью')
        ordering = ['-created_at']

    def __str__(self):
        return f'Заявка на интервью: {self.project_name} ({self.user})'


class DevelopmentCategory(models.Model):
    """
    Категории развития (навыки, компетенции)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name='Название категории')
    description = models.TextField(verbose_name='Описание')
    icon = models.CharField(max_length=50, verbose_name='Иконка')
    color = models.CharField(max_length=7, default='#007bff', verbose_name='Цвет')
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')

    class Meta:
        verbose_name = 'Категория развития'
        verbose_name_plural = 'Категории развития'
        ordering = ['name']

    def __str__(self):
        return self.name


class DevelopmentSkill(models.Model):
    """
    Конкретные навыки для развития
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(
        DevelopmentCategory,
        on_delete=models.CASCADE,
        related_name='skills',
        verbose_name='Категория'
    )
    name = models.CharField(max_length=100, verbose_name='Название навыка')
    description = models.TextField(verbose_name='Описание')
    difficulty_level = models.IntegerField(
        choices=[(1, 'Начальный'), (2, 'Средний'), (3, 'Продвинутый')],
        default=1,
        verbose_name='Уровень сложности'
    )
    estimated_time = models.CharField(
        max_length=50,
        help_text='Примерное время на освоение',
        verbose_name='Время освоения'
    )
    keywords = models.CharField(
        max_length=200,
        help_text='Ключевые слова через запятую',
        verbose_name='Ключевые слова'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')

    class Meta:
        verbose_name = 'Навык развития'
        verbose_name_plural = 'Навыки развития'
        ordering = ['category', 'difficulty_level', 'name']

    def __str__(self):
        return f"{self.category.name}: {self.name}"


class DevelopmentPath(models.Model):
    """
    Дорожка развития - последовательность навыков
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, verbose_name='Название дорожки')
    description = models.TextField(verbose_name='Описание')
    target_audience = models.TextField(verbose_name='Целевая аудитория')
    duration = models.CharField(max_length=50, verbose_name='Продолжительность')
    skills = models.ManyToManyField(
        DevelopmentSkill,
        related_name='development_paths',
        verbose_name='Навыки'
    )
    difficulty_level = models.IntegerField(
        choices=[(1, 'Начальный'), (2, 'Средний'), (3, 'Продвинутый')],
        default=1,
        verbose_name='Уровень сложности'
    )
    is_recommended = models.BooleanField(default=False, verbose_name='Рекомендуемая')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')

    class Meta:
        verbose_name = 'Дорожка развития'
        verbose_name_plural = 'Дорожки развития'
        ordering = ['order', 'title']

    def __str__(self):
        return self.title


class UserDevelopmentPlan(models.Model):
    """
    План развития пользователя
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='development_plans',
        verbose_name='Пользователь'
    )
    development_path = models.ForeignKey(
        DevelopmentPath,
        on_delete=models.CASCADE,
        related_name='user_plans',
        verbose_name='Дорожка развития'
    )
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата начала')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата завершения')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    progress_percentage = models.IntegerField(default=0, verbose_name='Прогресс (%)')
    notes = models.TextField(blank=True, verbose_name='Заметки')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')

    class Meta:
        verbose_name = 'План развития пользователя'
        verbose_name_plural = 'Планы развития пользователей'
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.user}: {self.development_path.title}"


class UserSkillProgress(models.Model):
    """
    Прогресс пользователя по конкретным навыкам
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='skill_progress',
        verbose_name='Пользователь'
    )
    skill = models.ForeignKey(
        DevelopmentSkill,
        on_delete=models.CASCADE,
        related_name='user_progress',
        verbose_name='Навык'
    )
    mastery_level = models.IntegerField(
        choices=[
            (0, 'Не начато'),
            (1, 'Начальный'),
            (2, 'Средний'),
            (3, 'Продвинутый'),
            (4, 'Эксперт')
        ],
        default=0,
        verbose_name='Уровень владения'
    )
    practice_hours = models.IntegerField(default=0, verbose_name='Часов практики')
    notes = models.TextField(blank=True, verbose_name='Заметки')
    last_practiced = models.DateTimeField(null=True, blank=True, verbose_name='Последняя практика')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')

    class Meta:
        verbose_name = 'Прогресс по навыку'
        verbose_name_plural = 'Прогресс по навыкам'
        unique_together = ['user', 'skill']
        ordering = ['-mastery_level', 'skill']

    def __str__(self):
        return f"{self.user}: {self.skill.name} ({self.get_mastery_level_display()})"


class DevelopmentResource(models.Model):
    """
    Ресурсы для развития (книги, курсы, статьи)
    """
    RESOURCE_TYPES = [
        ('book', 'Книга'),
        ('course', 'Курс'),
        ('article', 'Статья'),
        ('video', 'Видео'),
        ('tool', 'Инструмент'),
        ('practice', 'Практика')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    skill = models.ForeignKey(
        DevelopmentSkill,
        on_delete=models.CASCADE,
        related_name='resources',
        verbose_name='Навык'
    )
    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    resource_type = models.CharField(
        max_length=20,
        choices=RESOURCE_TYPES,
        verbose_name='Тип ресурса'
    )
    url = models.URLField(blank=True, verbose_name='Ссылка')
    difficulty_level = models.IntegerField(
        choices=[(1, 'Начальный'), (2, 'Средний'), (3, 'Продвинутый')],
        default=1,
        verbose_name='Уровень сложности'
    )
    estimated_time = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Время на изучение'
    )
    is_free = models.BooleanField(default=True, verbose_name='Бесплатный')
    is_recommended = models.BooleanField(default=False, verbose_name='Рекомендуемый')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')

    class Meta:
        verbose_name = 'Ресурс для развития'
        verbose_name_plural = 'Ресурсы для развития'
        ordering = ['skill', 'order', 'title']

    def __str__(self):
        return f"{self.skill.name}: {self.title}"


# ===== МОДЕЛИ ДЛЯ СИСТЕМЫ ОБРАТНОЙ СВЯЗИ =====


class FeedbackCategory(models.Model):
    """
    Категории обратной связи
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name='Название категории')
    description = models.TextField(blank=True, verbose_name='Описание')
    icon = models.CharField(max_length=50, default='💬', verbose_name='Иконка')
    color = models.CharField(max_length=7, default='#007bff', verbose_name='Цвет')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')

    class Meta:
        verbose_name = 'Категория обратной связи'
        verbose_name_plural = 'Категории обратной связи'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class UserFeedback(models.Model):
    """
    Обратная связь от пользователей
    """
    FEEDBACK_TYPES = [
        ('suggestion', 'Предложение'),
        ('complaint', 'Жалоба'),
        ('question', 'Вопрос'),
        ('compliment', 'Комплимент'),
        ('bug_report', 'Ошибка'),
        ('feature_request', 'Запрос функции'),
        ('improvement', 'Улучшение')
    ]

    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('in_review', 'На рассмотрении'),
        ('in_progress', 'В работе'),
        ('resolved', 'Решена'),
        ('rejected', 'Отклонена'),
        ('closed', 'Закрыта')
    ]

    PRIORITY_CHOICES = [
        (1, 'Низкий'),
        (2, 'Средний'),
        (3, 'Высокий'),
        (4, 'Критический')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='feedbacks',
        verbose_name='Пользователь'
    )
    category = models.ForeignKey(
        FeedbackCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name='feedbacks',
        verbose_name='Категория'
    )
    feedback_type = models.CharField(
        max_length=20,
        choices=FEEDBACK_TYPES,
        verbose_name='Тип обратной связи'
    )
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    message = models.TextField(verbose_name='Сообщение')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name='Статус'
    )
    priority = models.IntegerField(
        choices=PRIORITY_CHOICES,
        default=2,
        verbose_name='Приоритет'
    )
    email = models.EmailField(blank=True, verbose_name='Email для ответа')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    page_url = models.URLField(blank=True, verbose_name='URL страницы')
    user_agent = models.TextField(blank=True, verbose_name='User Agent')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP адрес')
    admin_notes = models.TextField(blank=True, verbose_name='Заметки администратора')
    admin_response = models.TextField(blank=True, verbose_name='Ответ администратора')
    responded_at = models.DateTimeField(null=True, blank=True, verbose_name='Время ответа')
    responded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='responded_feedbacks',
        verbose_name='Кто ответил'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')

    class Meta:
        verbose_name = 'Обратная связь'
        verbose_name_plural = 'Обратная связь'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    @property
    def is_anonymous(self):
        """Является ли отзыв анонимным"""
        return self.user is None

    @property
    def response_time_hours(self):
        """Время ответа в часах"""
        if self.responded_at:
            delta = self.responded_at - self.created_at
            return round(delta.total_seconds() / 3600, 2)
        return None


class FeedbackAttachment(models.Model):
    """
    Вложения к обратной связи
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    feedback = models.ForeignKey(
        UserFeedback,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name='Обратная связь'
    )
    file = models.FileField(
        upload_to='feedback_attachments/%Y/%m/',
        verbose_name='Файл'
    )
    filename = models.CharField(max_length=255, verbose_name='Имя файла')
    file_size = models.PositiveIntegerField(verbose_name='Размер файла (байты)')
    content_type = models.CharField(max_length=100, verbose_name='Тип файла')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')

    class Meta:
        verbose_name = 'Вложение к отзыву'
        verbose_name_plural = 'Вложения к отзывам'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.feedback.title}: {self.filename}"


class FeedbackRating(models.Model):
    """
    Оценка полезности ответа на обратную связь
    """
    RATING_CHOICES = [
        (1, '1 - Очень плохо'),
        (2, '2 - Плохо'),
        (3, '3 - Нормально'),
        (4, '4 - Хорошо'),
        (5, '5 - Отлично')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    feedback = models.OneToOneField(
        UserFeedback,
        on_delete=models.CASCADE,
        related_name='rating',
        verbose_name='Обратная связь'
    )
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        verbose_name='Оценка'
    )
    comment = models.TextField(blank=True, verbose_name='Комментарий к оценке')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')

    class Meta:
        verbose_name = 'Оценка обратной связи'
        verbose_name_plural = 'Оценки обратной связи'

    def __str__(self):
        return f"Оценка {self.rating} для {self.feedback.title}"


# ===== МОДЕЛИ ДЛЯ ПЕРСИСТЕНТНОСТИ СЕССИЙ ИИ КОНСУЛЬТАНТА =====


class ConversationState(models.Model):
    """
    💾 Модель для хранения состояний对话 ИИ консультанта
    Позволяет сохранять прогресс пользователя между сессиями
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_id = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text="Уникальный идентификатор сессии"
    )

    # Основные данные对话
    stage = models.CharField(
        max_length=50,
        choices=[
            ('welcome', 'Начало создания'),
            ('name', 'Название клуба'),
            ('category', 'Категория'),
            ('description', 'Описание'),
            ('city', 'Город'),
            ('email', 'Email для связи'),
            ('phone', 'Телефон'),
            ('confirm', 'Подтверждение'),
            ('edit', 'Редактирование'),
            ('done', 'Завершено'),
            ('error', 'Ошибка'),
        ],
        default='welcome',
        db_index=True,
        help_text="Текущий этап对话"
    )

    data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Данные, собранные на текущем этапе"
    )

    # Метаданные
    last_question = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Последний заданный вопрос"
    )

    progress = models.IntegerField(
        default=0,
        help_text="Прогресс в процентах (0-100)"
    )

    # Дополнительная информация
    user_agent = models.TextField(
        blank=True,
        null=True,
        help_text="User-Agent браузера"
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP адрес пользователя"
    )

    # Таймстемпы
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Время окончания жизни сессии"
    )

    # Связи с другими моделями
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conversation_states',
        help_text="Пользователь (если аутентифицирован)"
    )

    class Meta:
        db_table = 'ai_conversation_states'
        verbose_name = 'Состояние对话'
        verbose_name_plural = 'Состояния对话'
        indexes = [
            models.Index(fields=['session_id']),
            models.Index(fields=['stage']),
            models.Index(fields=['created_at']),
            models.Index(fields=['updated_at']),
            models.Index(fields=['expires_at']),
        ]
        ordering = ['-updated_at']

    def __str__(self):
        return f"Conversation {self.session_id[:8]}... - {self.stage}"

    def clean(self):
        """Валидация модели"""
        if self.progress < 0 or self.progress > 100:
            raise ValidationError('Progress должен быть в диапазоне 0-100')

    def save(self, *args, **kwargs):
        self.full_clean()  # Вызов clean() перед сохранением
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        """Проверка истекла ли сессия"""
        if self.expires_at:
            from django.utils import timezone
            return timezone.now() > self.expires_at
        # По умолчанию сессия истекает через 2 часа
        from django.utils import timezone
        return timezone.now() > self.created_at + timezone.timedelta(hours=2)

    @property
    def is_active(self):
        """Проверка активна ли сессия"""
        return not self.is_expired and self.stage != 'done'

    def extend_expiration(self, hours=2):
        """Продлить время жизни сессии"""
        from django.utils import timezone
        self.expires_at = timezone.now() + timezone.timedelta(hours=hours)
        self.save(update_fields=['expires_at'])

    def get_data_field(self, field, default=None):
        """Безопасное получение поля из JSON данных"""
        if isinstance(self.data, dict):
            return self.data.get(field, default)
        return default

    def set_data_field(self, field, value):
        """Безопасное установка поля в JSON данные"""
        if not isinstance(self.data, dict):
            self.data = {}
        self.data[field] = value
        self.save(update_fields=['data', 'updated_at'])

    def get_progress_percentage(self):
        """Получить прогресс в процентах на основе этапа"""
        stage_progress = {
            'welcome': 0,
            'name': 12,
            'category': 25,
            'description': 37,
            'city': 50,
            'email': 62,
            'phone': 75,
            'confirm': 100,
            'edit': 50,  # При редактировании средний прогресс
            'done': 100,
            'error': 0,
        }
        return stage_progress.get(self.stage, 0)

    def update_progress(self):
        """Обновить прогресс на основе текущего этапа"""
        self.progress = self.get_progress_percentage()
        self.save(update_fields=['progress', 'updated_at'])


class AISessionLog(models.Model):
    """
    📋 Логирование сессий ИИ для аналитики и отладки
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_id = models.CharField(
        max_length=255,
        db_index=True,
        help_text="ID сессии ИИ"
    )

    # Тип лога
    LOG_TYPES = [
        ('user_input', 'Ввод пользователя'),
        ('ai_response', 'Ответ ИИ'),
        ('error', 'Ошибка'),
        ('validation', 'Валидация'),
        ('security', 'Событие безопасности'),
        ('state_change', 'Изменение состояния'),
    ]

    log_type = models.CharField(
        max_length=20,
        choices=LOG_TYPES,
        db_index=True,
        help_text="Тип лога"
    )

    # Содержимое
    message = models.TextField(help_text="Сообщение или данные")
    response_data = models.JSONField(
        null=True,
        blank=True,
        help_text="Данные ответа (для AI responses)"
    )

    # Метаданные
    processing_time = models.FloatField(
        null=True,
        blank=True,
        help_text="Время обработки в секундах"
    )

    tokens_used = models.IntegerField(
        null=True,
        blank=True,
        help_text="Количество использованных токенов"
    )

    stage = models.CharField(
        max_length=50,
        blank=True,
        db_index=True,
        help_text="Этап对话"
    )

    # Техническая информация
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True
    )

    user_agent = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_session_logs'
        verbose_name = 'Лог сессии ИИ'
        verbose_name_plural = 'Логи сессий ИИ'
        indexes = [
            models.Index(fields=['session_id', 'created_at']),
            models.Index(fields=['log_type']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.log_type}: {self.session_id[:8]}... - {self.created_at}"


class ClubCreationRequest(models.Model):
    """
    🏗️ Запросы на создание клубов для отслеживания
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_state = models.OneToOneField(
        ConversationState,
        on_delete=models.CASCADE,
        related_name='creation_request'
    )

    # Данные клуба
    club_name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    description = models.TextField()
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    # Статус обработки
    STATUS_CHOICES = [
        ('pending', 'В обработке'),
        ('success', 'Успешно создан'),
        ('failed', 'Ошибка создания'),
        ('cancelled', 'Отменено'),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True
    )

    # Результат
    club_id = models.UUIDField(
        null=True,
        blank=True,
        help_text="ID созданного клуба"
    )

    error_message = models.TextField(
        blank=True,
        null=True,
        help_text="Сообщение об ошибке"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'club_creation_requests'
        verbose_name = 'Запрос создания клуба'
        verbose_name_plural = 'Запросы создания клубов'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"Club creation: {self.club_name} - {self.status}"


# Сигналы для автоматической очистки старых сессий
from django.db.models.signals import post_delete
from django.dispatch import receiver

@receiver(post_delete, sender=ConversationState)
def cleanup_session_logs(sender, instance, **kwargs):
    """Удаляем логи при удалении состояния сессии"""
    AISessionLog.objects.filter(session_id=instance.session_id).delete()