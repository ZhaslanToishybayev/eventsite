import re
import uuid
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, FileExtensionValidator
from django.db import models
from django.urls import reverse
from .managers import UserManager  # Импорт менеджера из другого файла
from django.core.exceptions import ValidationError


def phone_regex_validator(value):
    """
    Валидатор для проверки, что номер телефона начинается с определённых префиксов.

    Параметры:
        value (str): Значение поля номера телефона.

    Исключения:
        ValidationError: Если номер телефона не соответствует требованиям.
    """
    valid_prefixes = ('+770', '+7747', '+7771', '+7775', '+7776', '+7777', '+7778')
    phone_regex = re.compile(r'^\+7\d{9,12}$')  # Проверка формата +7XXXXXXXXXX

    if not phone_regex.match(value):
        raise ValidationError(
            _("Invalid phone number format. It must start with '+7' and have 11-14 digits.")
        )

    if not any(value.startswith(prefix) for prefix in valid_prefixes):
        raise ValidationError(
            _("The phone number must start with one of the following prefixes: %(prefixes)s"),
            params={'prefixes': ', '.join(valid_prefixes)},
        )


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(_("first name"), max_length=150)
    last_name = models.CharField(_("last name"), max_length=150)
    avatar = models.ImageField(
        upload_to="user/avatars/",
        default='user/avatars/user.png',
        blank=True,
        verbose_name='Фото',
        validators=[FileExtensionValidator(['png', 'jpg', 'jpeg'])]
    )
    phone = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Номер телефона",
        validators=[phone_regex_validator]
    )
    email = models.EmailField(unique=True, null=True)
    is_displayed_in_allies = models.BooleanField(default=False)
    can_create_clubs = models.BooleanField(default=False)

    username = None

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    def __str__(self):
        if self.first_name and self.last_name:
            return self.first_name + ' ' + self.last_name
        else:
            return self.phone

    def get_absolute_url(self):
        return reverse('user_detail', kwargs={'pk': self.pk})

    def get_formatted_phone(self):
        return self.phone.split('+')[1]

    def save(self, *args, **kwargs):
        if not self.email:
            self.email = None
        super().save(*args, **kwargs)

    def get_active_managed_clubs(self):
        return self.managed_clubs.filter(is_active=True)

    def get_active_membered_clubs(self):
        return self.members_of_clubs.filter(is_active=True)


class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        'accounts.User',
        verbose_name='Пользователь',
        related_name='profile',
        on_delete=models.CASCADE
    )
    about = models.TextField(null=True, blank=True, verbose_name='О себе')
    goals_for_life = models.TextField(null=True, blank=True, verbose_name='Цели на жизнь')
    interests = models.TextField(null=True, blank=True, verbose_name='Интересы')
    city = models.CharField(max_length=100, null=True, blank=True, verbose_name='Город')
    first_visit_completed = models.BooleanField(default=False, verbose_name='Первый визит завершен')
    welcome_chat_session_created = models.BooleanField(default=False, verbose_name='Приветственная сессия создана')
