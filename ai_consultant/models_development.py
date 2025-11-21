from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


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