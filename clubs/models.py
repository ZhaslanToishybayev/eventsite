import datetime
import uuid

from django.core.validators import MinLengthValidator, FileExtensionValidator
from django.db import models
from django.urls import reverse
from ckeditor_uploader.fields import RichTextUploadingField
from bs4 import BeautifulSoup
from pytz import timezone
from accounts.models import phone_regex_validator
from core.validators import secure_image_validator


class ClubCategory(models.Model):
    """
    Модель представляет категорию клуба.

    Attributes:
        id (UUIDField): Уникальный идентификатор категории (автоматически генерируется).
        name (CharField): Название категории.
        is_active (BooleanField): Флаг, указывающий, активна ли категория.
        created_at (DateTimeField): Дата и время создания категории (автоматически устанавливается).
        updated_at (DateTimeField): Дата и время последнего обновления категории (автоматически устанавливается).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, verbose_name='Название категории')
    is_active = models.BooleanField(default=True, verbose_name='Активность')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создана')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлена')

    def delete(self, *args, **kwargs):
        """
        Помечает категорию как неактивную вместо фактического удаления из базы данных.
        """
        self.is_active = False
        self.save()

    def __str__(self):
        """
        Возвращает строковое представление названия категории.
        """
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'pk': self.pk})


class City(models.Model):
    """
    Модель представляет город.

    Attributes:
        id (UUIDField): Уникальный идентификатор города (автоматически генерируется).
        iata_code (CharField): Код города (ИАТА).
        name (CharField): Название города.
        created_at (DateTimeField): Дата и время создания записи о городе (автоматически устанавливается).
        updated_at (DateTimeField): Дата и время последнего обновления записи о городе (автоматически устанавливается).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    iata_code = models.CharField(max_length=20, db_index=True, verbose_name='Код города')
    name = models.CharField(max_length=50, verbose_name='Название города')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлен')

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'

    def __str__(self):
        """
        Возвращает строковое представление названия города.
        """
        return self.name


class Club(models.Model):
    """
    Модель представляет клуб.

    Attributes:
        id (UUIDField): Уникальный идентификатор клуба (автоматически генерируется).
        name (CharField): Имя клуба.
        category (ForeignKey): Категория клуба.
        logo (ImageField): Логотип клуба.
        creater (ForeignKey): Создатель клуба.
        managers (ManyToManyField): Управляющие клуба.
        description (TextField): Описание клуба.
        email (EmailField): Контактный email клуба.
        phone (CharField): Контактный телефон клуба.
        city (ForeignKey): Город, к которому относится клуб.
        address (CharField): Локация клуба.
        members (ManyToManyField): Члены клуба.
        members_count (PositiveIntegerField): Количество участников клуба.
        likes_count (PositiveIntegerField): Количество лайков клуба.
        is_active (BooleanField): Флаг, указывающий, активен ли клуб.
        is_private (BooleanField): Флаг, указывающий, является ли клуб приватным.
        created_at (DateTimeField): Дата и время создания клуба (автоматически устанавливается).
        updated_at (DateTimeField): Дата и время последнего обновления клуба (автоматически устанавливается).
        likes (ManyToManyField): Пользователи, лайкнувшие клуб.
        partners (ManyToManyField): Клубы-партнеры.
        partners_count (PositiveIntegerField): Количество партнеров клуба.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, verbose_name='Имя сообщества')
    category = models.ForeignKey(
        'clubs.ClubCategory',
        on_delete=models.PROTECT,
        related_name='clubs',
        verbose_name='Категория',
        limit_choices_to={'is_active': True},
    )
    logo = models.ImageField(
        upload_to='club/logos',
        validators=[FileExtensionValidator(['png', 'jpg', 'jpeg'])],
        default='club/logos/club-icon.png',
        verbose_name='Логотип'
    )
    whatsapp_group_link = models.URLField(verbose_name='Ссылка на группу Whatsapp', null=True, blank=True)
    creater = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='created_clubs',
    )
    managers = models.ManyToManyField(
        'accounts.User',
        related_name='managed_clubs',
        blank=True,
        verbose_name='Управляющие клуба'
    )
    description = models.TextField(validators=[MinLengthValidator(200)], verbose_name='Описание')
    email = models.EmailField(verbose_name='Контактный email')
    phone = models.CharField(validators=[phone_regex_validator], verbose_name='Контактный телефон', max_length=20)
    city = models.ForeignKey(
        to='clubs.City',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clubs',
        verbose_name='Город'
    )
    address = models.CharField(default='No location', verbose_name='Локация клуба', max_length=150, blank=True)
    members = models.ManyToManyField(
        'accounts.User',
        verbose_name='Члены клуба',
        related_name='members_of_clubs',
        blank=True,
    )
    members_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Кол-во участников',
        editable=False,
    )
    likes_count = models.PositiveIntegerField(default=0, verbose_name='Кол-во лайков', editable=False)
    is_active = models.BooleanField(default=True, verbose_name='Активность')
    is_private = models.BooleanField(default=False, verbose_name='Приватный клуб')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлен')
    likes = models.ManyToManyField(
        to='accounts.User',
        verbose_name='Лайкнули',
        related_name='liked_by_users',
        blank=True,
    )
    partners = models.ManyToManyField(
        to='self',
        verbose_name='Клубы-партнеры',
        related_name='club_partners',
        blank=True,
        symmetrical=True,
    )
    partners_count = models.PositiveIntegerField(default=0, verbose_name='Кол-во партнеров', editable=False)

    # Поля для рекомендательной системы
    tags = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Теги (через запятую)',
        help_text='Например: спорт, здоровье, развитие, технологии'
    )
    target_audience = models.TextField(
        blank=True,
        verbose_name='Целевая аудитория',
        help_text='Описание идеальных участников клуба'
    )
    activities = models.TextField(
        blank=True,
        verbose_name='Мероприятия',
        help_text='Какие мероприятия проводит клуб'
    )
    skills_developed = models.TextField(
        blank=True,
        verbose_name='Развиваемые навыки',
        help_text='Какие навыки участники развивают в клубе'
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name='Рекомендуемый клуб',
        help_text='Показывать в рекомендациях'
    )
    recommendation_score = models.PositiveIntegerField(
        default=0,
        verbose_name='Оценка рекомендаций',
        help_text='Чем выше, тем чаще клуб появляется в рекомендациях'
    )

    def __str__(self):
        """
        Возвращает строковое представление имени клуба.
        """
        return self.name

    def get_absolute_url(self):
        return reverse('club_detail', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = 'Клуб'
        verbose_name_plural = 'Клубы'
        ordering = ('-members_count', '-likes_count', 'name')

    def delete(self, using=None, keep_parents=False):
        """
        Помечает клуб как неактивный вместо фактического удаления из базы данных.
        """
        self.is_active = False
        self.save()

    def get_gallery_url(self):
        return reverse('club_photogallery', kwargs={'pk': self.pk})

    def get_managers_phone_str(self):
        phones = ', '.join(manager.phone[:20] for manager in self.managers.all() if manager.phone)
        return phones

    def get_managers_email_str(self):
        emails = ', '.join(manager.email for manager in self.managers.all() if manager.email)
        return emails


class ClubJoinRequest(models.Model):
    """
    Модель представляет запрос на вступление пользователя в клуб, у которого is_private=True.

    Attributes:
        id (UUIDField): Уникальный идентификатор запроса (автоматически генерируется).
        user (ForeignKey): Пользователь, отправивший запрос.
        club (ForeignKey): Клуб, в который отправлен запрос.
        approved (BooleanField): Флаг, указывающий, принят ли запрос.
        created_at (DateTimeField): Дата и время создания запроса (автоматически устанавливается).
        updated_at (DateTimeField): Дата и время последнего обновления запроса (автоматически устанавливается).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        to='accounts.User',
        on_delete=models.CASCADE,
        related_name='user_join_requests',
        verbose_name='Пользователь'
    )
    club = models.ForeignKey(
        to='clubs.Club',
        on_delete=models.CASCADE,
        related_name='club_join_requests',
        verbose_name='Клуб'
    )
    approved = models.BooleanField(default=None, null=True, verbose_name='Принят')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        Возвращает строковое представление объекта запроса на вступление.

        Returns:
            str: Строковое представление объекта, содержащее информацию о пользователе и клубе.
        """
        return f'Запрос на вступление: {self.user} -> {self.club}'

    class Meta:
        verbose_name = 'Запрос на вступление в клуб'
        verbose_name_plural = 'Запросы на вступление в клуб'
        constraints = [
            models.UniqueConstraint(fields=['user', 'club'], name='unique_user_club_join_request')
        ]


class ClubPartnerShipRequest(models.Model):
    """
    Модель представляет запрос на партнерство между клубами.

    Attributes:
        id (UUIDField): Уникальный идентификатор запроса (автоматически генерируется).
        club_requester (ForeignKey): Клуб, отправляющий запрос на партнерство.
        club_accepter (ForeignKey): Клуб, принимающий запрос на партнерство.
        created_at (DateTimeField): Дата и время создания запроса на партнерство (автоматически устанавливается).
        updated_at (DateTimeField): Дата и время последнего обновления запроса на партнерство (автоматически устанавливается).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    club_requester = models.ForeignKey(
        to='clubs.Club',
        on_delete=models.CASCADE,
        related_name='partnership_send_requests',
        verbose_name='Запрашивающий клуб',
    )
    club_accepter = models.ForeignKey(
        to='clubs.Club',
        on_delete=models.CASCADE,
        related_name='partnership_receive_requests',
        verbose_name='Принимающий клуб',
    )
    approved = models.BooleanField(verbose_name='Принято', null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        Возвращает строковое представление запроса на партнерство между клубами.
        """
        return f'Запрос на партнерство: {self.club_requester} -> {self.club_accepter}'


class ClubService(models.Model):
    """
    Модель представляет услугу клуба.

    Attributes:
        id (UUIDField): Уникальный идентификатор услуги (автоматически генерируется).
        club (ForeignKey): Клуб, к которому относится услуга.
        name (CharField): Название услуги.
        description (TextField): Описание услуги.
        price (DecimalField): Цена услуги.
        created_at (DateTimeField): Дата и время создания услуги (автоматически устанавливается).
        updated_at (DateTimeField): Дата и время последнего обновления услуги (автоматически устанавливается).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    club = models.ForeignKey(
        'clubs.Club',
        on_delete=models.CASCADE,
        related_name='services',
        verbose_name='Клуб',
        limit_choices_to={'is_active': True},
    )
    name = models.CharField(max_length=100, unique=True, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')

    def __str__(self):
        """
        Возвращает строковое представление названия услуги.
        """
        return self.name

    @property
    def get_first_img(self):
        """
        Получает первое изображение услуги.

        Оптимизировано для работы с prefetch_related - сначала проверяет
        уже загруженные изображения, только потом делает запрос к БД.
        """
        # Проверяем, есть ли уже загруженные изображения (при использовании prefetch_related)
        if hasattr(self, '_prefetched_objects_cache') and 'images' in self._prefetched_objects_cache:
            images = self.images.all()
            return images.first() if images.exists() else None

        # Если изображения не были загружены, делаем отдельный запрос (обратная совместимость)
        return ClubServiceImage.objects.filter(service=self).first()

    class Meta:
        verbose_name = 'Услуга клуба'
        verbose_name_plural = 'Услуги клуба'


class ServiceForClubs(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name="Наименование услуги")
    description = models.CharField(max_length=200, verbose_name="Описание услуги")
    min_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена от(KZT.)', blank=True, null=True)
    max_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена до(KZT.)', blank=True, null=True)
    phone = models.CharField(
        max_length=20,
        verbose_name="Контактный телефон",
        validators=[phone_regex_validator]
    )
    image = models.ImageField(upload_to='clubs/service_for_clubs', verbose_name='Фото')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')

    def __str__(self):
        return f'Услуга для сообществ - {self.name}'

    def get_absolute_url(self):
        return reverse('service_for_club_detail', kwargs={'pk': self.pk})

    def get_price_range_str(self):
        if self.min_price and self.max_price:
            return f'от {self.min_price} - до {self.max_price} KZT.'
        if self.min_price:
            return f'от {self.min_price} KZT.'
        if self.max_price:
            return f'до {self.max_price} KZT.'
        return f'Договорная'

    class Meta:
        verbose_name = 'Услуга для сообществ'
        verbose_name_plural = 'Услуги для сообществ'


class ClubServiceImage(models.Model):
    """
    Модель представляет изображение для услуги клуба.

    Attributes:
        id (UUIDField): Уникальный идентификатор изображения (автоматически генерируется).
        club (ForeignKey): Услуга клуба, к которой относится изображение.
        image (ImageField): Файл изображения.
        created_at (DateTimeField): Дата и время создания изображения (автоматически устанавливается).
        updated_at (DateTimeField): Дата и время последнего обновления изображения (автоматически устанавливается).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.ForeignKey(to='clubs.ClubService', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(
        upload_to='club/service_images',
        validators=[FileExtensionValidator(['png', 'jpg', 'jpeg'])],
        verbose_name='Фото'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')

    def __str__(self):
        """
        Возвращает строковое представление изображения.
        """
        return f"Изображение для {self.service.name}"

    class Meta:
        verbose_name = 'Изображение для услуги клуба'
        verbose_name_plural = 'Изображения для услуг клуба'
        

class ClubGalleryPhoto(models.Model):
    """
    Модель представляет фотографию в галерее клуба.

    Attributes:
        id (UUIDField): Уникальный идентификатор фотографии (автоматически генерируется).
        club (ForeignKey): Клуб, к которому относится фотография.
        image (ImageField): Файл изображения.
        created_at (DateTimeField): Дата и время создания фотографии (автоматически устанавливается).
        updated_at (DateTimeField): Дата и время последнего обновления фотографии (автоматически устанавливается).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    club = models.ForeignKey(
        to='clubs.Club',
        on_delete=models.CASCADE,
        related_name='gallery_photos',
        verbose_name='Клуб'
    )
    image = models.ImageField(upload_to='clubs/gallery', verbose_name='Фото')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        Возвращает строковое представление фотографии, состоящее из названия клуба и названия изображения.
        """
        return f'{self.club.name}-{self.image.name}'

    class Meta:
        verbose_name = "Фото"
        verbose_name_plural = "Фото"
        ordering = ('-created_at',)


class ClubEvent(models.Model):
    """
    Модель представляет событие клуба.

    Attributes:
        id (UUIDField): Уникальный идентификатор события (автоматически генерируется).
        club (ForeignKey): Клуб, к которому относится событие.
        title (CharField): Название события.
        description (TextField): Описание события.
        banner (ImageField): Баннер события.
        location (CharField): Место проведения события.
        start_datetime (DateTimeField): Дата и время начала события.
        old_datetime (DateTimeField): Дата и время старта, если событие является переносом.
        end_datetime (DateTimeField): Дата и время завершения события.
        min_age (PositiveIntegerField): Минимальный возраст для входа на событие.
        max_age (PositiveIntegerField): Максимальный возраст для входа на событие.
        entry_requirements (TextField): Требования для входа на событие.
        created_at (DateTimeField): Дата и время создания записи о событии (автоматически устанавливается).
        updated_at (DateTimeField): Дата и время последнего обновления записи о событии (автоматически устанавливается).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    club = models.ForeignKey(
        to='clubs.Club',
        on_delete=models.CASCADE,
        related_name='club_events',
        verbose_name='Клуб'
    )
    title = models.CharField(max_length=150, verbose_name='Название события')
    description = models.TextField(verbose_name='Описание')
    banner = models.ImageField(upload_to='clubs/event_banners', verbose_name='Баннер события')
    location = models.CharField(max_length=150, verbose_name='Место проведения')
    start_datetime = models.DateTimeField(verbose_name='Дата и время начала')
    old_datetime = models.DateTimeField(blank=True, null=True)
    end_datetime = models.DateTimeField(verbose_name='Дата и время завершения')
    min_age = models.PositiveIntegerField(blank=True, null=True, verbose_name='Минимальный возраст для входа')
    max_age = models.PositiveIntegerField(blank=True, null=True, verbose_name='Максимальный возраст для входа')
    entry_requirements = models.TextField(blank=True, null=True, verbose_name='Требования для входа')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        Возвращает строковое представление названия события.
        """
        return self.title

    @property
    def is_passed(self):
        return datetime.datetime.now(tz=timezone('UTC')) > self.start_datetime

    class Meta:
        verbose_name = "Событие"
        verbose_name_plural = "События"

    def get_age_restriction_str(self):
        if self.min_age is None and self.max_age is None:
            return 'Без ограничении'
        if self.min_age is None and self.max_age:
            return f'Лицам до {self.max_age}'
        if self.min_age and self.max_age is None:
            return f'Лицам с {self.min_age}'
        if self.min_age and self.max_age:
            return f'{self.min_age} - {self.max_age}'

    def get_entry_restriction_str(self):
        if self.entry_requirements is None:
            return 'Требовании нет'
        return self.entry_requirements

    def get_absolute_url(self):
        return reverse('event_detail', kwargs={'pk': self.pk})


class ClubAdType(models.Model):
    """
    Модель представляет тип объявления клуба.

    Attributes:
        id (UUIDField): Уникальный идентификатор типа объявления (автоматически генерируется).
        name (CharField): Название типа объявления.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name='Название')

    def __str__(self):
        """
        Возвращает строковое представление названия типа объявления.
        """
        return self.name


class ClubAds(models.Model):
    """
    Модель представляет объявление клуба.

    Attributes:
        id (UUIDField): Уникальный идентификатор объявления (автоматически генерируется).
        club (ForeignKey): Клуб, к которому относится объявление.
        type (ForeignKey): Тип объявления.
        title (CharField): Название объявления.
        description (TextField): Описание объявления.
        img (ImageField): Фото объявления.
        created_at (DateTimeField): Дата и время создания объявления (автоматически устанавливается).
        updated_at (DateTimeField): Дата и время последнего обновления объявления (автоматически устанавливается).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    club = models.ForeignKey(
        to='clubs.Club',
        on_delete=models.CASCADE,
        related_name='club_ads',
        verbose_name='Клуб'
    )
    type = models.ForeignKey(to='clubs.ClubAdType', on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=150, verbose_name='Название события')
    description = models.TextField(verbose_name='Описание')
    img = models.ImageField(upload_to='clubs/ad_photos', verbose_name='Фото объявления')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        Возвращает строковое представление названия объявления.
        """
        return self.title

    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'


class Festival(models.Model):
    """
    Модель представляет фестиваль.

    Attributes:
        id (UUIDField): Уникальный идентификатор фестиваля (автоматически генерируется).
        name (CharField): Заголовок фестиваля.
        description (TextField): Описание фестиваля.
        image (ImageField): Фото фестиваля.
        created_at (DateTimeField): Дата и время создания записи о фестивале (автоматически устанавливается).
        updated_at (DateTimeField): Дата и время последнего обновления записи о фестивале (автоматически устанавливается).
        location (CharField): Место проведения фестиваля.
        approved_clubs (ManyToManyField): Приглашенные клубы на фестиваль.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    image = models.ImageField(
        verbose_name='Фото',
        upload_to='clubs/festival_photo',
        validators=[FileExtensionValidator(['png', 'jpg', 'jpeg'])],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    start_datetime = models.DateTimeField(verbose_name='Дата начала')
    location = models.CharField(max_length=200, verbose_name='Локация')
    approved_clubs = models.ManyToManyField(
        to='clubs.Club',
        related_name='approved_on_festival',
        verbose_name='Приглашенные клубы',
        blank=True
    )

    class Meta:
        verbose_name_plural = 'Фестивали'
        verbose_name = 'Фестиваль'

    def __str__(self):
        """
        Возвращает строковое представление названия фестиваля.
        """
        return self.name

    def get_absolute_url(self):
        return reverse('festival_detail', kwargs={'pk': self.pk})

    def get_not_approved_clubs(self):
        return self.requests.exclude(approved=True)


class FestivalParticipationRequest(models.Model):
    """
    Модель представляет запрос на участие клуба в фестивале.

    Attributes:
        id (UUIDField): Уникальный идентификатор запроса (автоматически генерируется).
        club (ForeignKey): Клуб, отправляющий запрос.
        festival (ForeignKey): Фестиваль, на который отправлен запрос.
        approved (BooleanField): Флаг, указывающий, одобрен ли запрос.
        created_at (DateTimeField): Дата и время создания запроса (автоматически устанавливается).
        updated_at (DateTimeField): Дата и время последнего обновления запроса (автоматически устанавливается).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    club = models.ForeignKey(
        to='clubs.Club',
        on_delete=models.CASCADE,
        related_name='festival_participation_request'
    )
    festival = models.ForeignKey(
        to='clubs.Festival',
        on_delete=models.CASCADE,
        related_name='requests',
    )
    approved = models.BooleanField(default=None, null=True, verbose_name='Приглашен')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        Возвращает строковое представление запроса на участие в фестивале.
        """
        return f'{self.club.name} - {self.festival.name}'

    @property
    def request_status_str(self):
        if self.approved:
            return 'Принят'
        if self.approved is None:
            return 'В ожидании'
        if not self.approved:
            return 'Отклонен'

    class Meta:
        verbose_name_plural = 'Запросы на участие в фестивале'
        verbose_name = 'Запрос на участие в фестивале'
        constraints = [
            models.UniqueConstraint(fields=['club', 'festival'], name='unique_club_festival_request')
        ]


class Publication(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, verbose_name='Заголовок', unique=True)
    annotation = models.TextField(verbose_name='Краткое содержание')
    content = RichTextUploadingField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ['-created_at',]

    def get_absolute_url(self):
        return reverse('publication_detail', kwargs={'pk': self.pk})


class ClubPost(models.Model):
    """
    Модель представляет новостной пост клуба.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    club = models.ForeignKey(
        to='clubs.Club',
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Клуб'
    )
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    content = RichTextUploadingField(verbose_name='Содержание')
    is_published = models.BooleanField(default=True, verbose_name='Опубликовано')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлен')

    class Meta:
        verbose_name = 'Пост клуба'
        verbose_name_plural = 'Посты клуба'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.club.name}: {self.title}"
