from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import ChatSession, ChatMessage
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def user_created_handler(sender, instance, created, **kwargs):
    """
    Обработчик создания нового пользователя
    """
    if created:
        logger.info(f"Новый пользователь зарегистрирован: {instance.phone}")
        # Здесь можно добавить логику приветствия нового пользователя


@receiver(post_save, sender=ChatMessage)
def chat_message_created_handler(sender, instance, created, **kwargs):
    """
    Обработчик создания нового сообщения в чате
    """
    if created:
        user_identifier = instance.session.user.phone if instance.session.user else "Анонимный пользователь"
        logger.info(
            f"Новое сообщение в чате: {user_identifier} -> {instance.role}"
        )

        # Здесь можно добавить аналитику или триггеры
        if instance.role == 'user':
            # Счетчик сообщений пользователя
            pass