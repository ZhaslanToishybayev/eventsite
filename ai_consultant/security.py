# 🔐 МОДУЛЬ БЕЗОПАСНОСТИ ИИ КОНСУЛЬТАНТА
# Защита от XSS, валидация данных, фильтрация контента

import re
import html
import bleach
from django.core.exceptions import ValidationError
from django.core.validators import validate_email, RegexValidator
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class SecurityValidator:
    """Класс для валидации и очистки пользовательских данных"""

    # Список запрещенных слов (мат, оскорбления)
    FORBIDDEN_WORDS = [
        # Русские матерные слова (образец для демонстрации)
        'блядь', 'сука', 'хуй', 'пизда', 'ебать', 'блять',
        # Добавьте больше слов по необходимости
    ]

    # Список подозрительных паттернов (спам, фишинг)
    SPAM_PATTERNS = [
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
        r'(?i)(?:click|переходи|следуй)\s+(?:здесь|тут|по\s+ссылке)',
        r'(?i)(?:бесплатно|free)\s+(?:деньги|money|\$)',
        r'(?i)(?:win|победи|выиграй)\s+(?:prize|приз)',
    ]

    # Допустимые HTML теги для bleach
    ALLOWED_TAGS = ['b', 'i', 'u', 'strong', 'em', 'p', 'br']
    ALLOWED_ATTRIBUTES = {}
    ALLOWED_STYLES = []

    @classmethod
    def sanitize_html(cls, text: str) -> str:
        """
        Очистка HTML от потенциально опасного кода

        Args:
            text: Входной текст от пользователя

        Returns:
            Очищенный безопасный текст
        """
        if not text:
            return ""

        try:
            # Сначала экранируем HTML
            escaped = html.escape(text)

            # Затем разрешаем безопасные теги с помощью bleach
            cleaned = bleach.clean(
                escaped,
                tags=cls.ALLOWED_TAGS,
                attributes=cls.ALLOWED_ATTRIBUTES,
                styles=cls.ALLOWED_STYLES,
                strip=True
            )

            logger.info(f"HTML sanitized successfully, length: {len(text)} -> {len(cleaned)}")
            return cleaned

        except Exception as e:
            logger.error(f"HTML sanitization error: {e}")
            return html.escape(text)  # Fallback к простому экранированию

    @classmethod
    def validate_content(cls, text: str) -> tuple[bool, str]:
        """
        Валидация контента на спам и нецензурную лексику

        Args:
            text: Текст для проверки

        Returns:
            (is_valid, error_message)
        """
        if not text:
            return True, ""

        # Проверка на запрещенные слова
        text_lower = text.lower()
        for word in cls.FORBIDDEN_WORDS:
            if word in text_lower:
                logger.warning(f"Forbidden word detected: {word}")
                return False, "Текст содержит недопустимые слова"

        # Проверка на спам-паттерны
        for pattern in cls.SPAM_PATTERNS:
            if re.search(pattern, text_lower):
                logger.warning(f"Spam pattern detected: {pattern}")
                return False, "Текст похож на спам"

        # Дополнительная проверка на чрезмерное количество ссылок
        url_count = len(re.findall(r'http[s]?://', text_lower))
        if url_count > 2:
            return False, "Слишком много ссылок в тексте"

        return True, ""

    @classmethod
    def validate_email_advanced(cls, email: str) -> tuple[bool, str]:
        """
        Расширенная валидация email

        Args:
            email: Email для проверки

        Returns:
            (is_valid, error_message)
        """
        if not email:
            return False, "Email обязателен"

        try:
            # Базовая валидация Django
            validate_email(email)
        except ValidationError:
            return False, "Некорректный формат email"

        # Дополнительные проверки
        email_lower = email.lower()

        # Проверка на disposable email домены
        disposable_domains = [
            '10minutemail.com', 'tempmail.org', 'guerrillamail.com',
            'mailinator.com', 'yopmail.com', 'throwaway.email'
        ]

        domain = email_lower.split('@')[-1]
        if domain in disposable_domains:
            return False, "Временные email не разрешены"

        # Проверка на подозрительные паттерны
        suspicious_patterns = [
            r'[0-9]{5,}@',  # Много цифр перед @
            r'[a-z]{1,2}[0-9]{3,}@',  # Подозрительные комбинации
        ]

        for pattern in suspicious_patterns:
            if re.match(pattern, email_lower):
                logger.warning(f"Suspicious email pattern: {email}")
                return False, "Подозрительный email адрес"

        return True, ""

    @classmethod
    def validate_phone_advanced(cls, phone: str) -> tuple[bool, str]:
        """
        Расширенная валидация телефона

        Args:
            phone: Номер телефона для проверки

        Returns:
            (is_valid, error_message)
        """
        if not phone:
            return False, "Телефон обязателен"

        # Удаляем все символы кроме цифр
        digits_only = re.sub(r'[^\d]', '', phone)

        # Проверка длины номера
        if len(digits_only) < 10:
            return False, "Слишком короткий номер телефона"
        if len(digits_only) > 15:
            return False, "Слишком длинный номер телефона"

        # Проверка на валидные коды стран
        valid_country_codes = ['7', '1', '86', '44', '49', '33', '81', '91']
        first_digit = digits_only[0]

        # Для номеров, начинающихся с 7 (Казахстан/Россия)
        if first_digit == '7':
            if len(digits_only) != 11:
                return False, "Неверный формат номера для Казахстана/России"
            # Проверка кодов операторов
            operator_codes = ['700', '701', '702', '705', '707', '708', '747', '750', '751', '760', '761', '762', '763', '764', '771', '775', '776', '777', '778']
            code = digits_only[1:4]
            if code not in operator_codes:
                logger.warning(f"Susppecting operator code: {code}")
                # Не блокируем, но логируем

        return True, ""

    @classmethod
    def sanitize_ai_response(cls, response: str) -> str:
        """
        Очистка ответа от ИИ (безопасность для пользователя)

        Args:
            response: Ответ от ИИ

        Returns:
            Безопасный ответ для пользователя
        """
        if not response:
            return ""

        # Очищаем HTML
        cleaned = cls.sanitize_html(response)

        # Дополнительная проверка на потенциально опасный контент от ИИ
        dangerous_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',  # onclick, onload и т.д.
        ]

        for pattern in dangerous_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE | re.DOTALL)

        return cleaned

    @classmethod
    def validate_message_length(cls, message: str, min_length: int = 1, max_length: int = 10000) -> tuple[bool, str]:
        """
        Валидация длины сообщения

        Args:
            message: Сообщение для проверки
            min_length: Минимальная длина
            max_length: Максимальная длина

        Returns:
            (is_valid, error_message)
        """
        if not message or len(message.strip()) < min_length:
            return False, f"Сообщение должно содержать минимум {min_length} символов"

        if len(message) > max_length:
            return False, f"Сообщение слишком длинное (максимум {max_length} символов)"

        return True, ""

def sanitize_user_input(data: str) -> str:
    """
    Удобная функция для очистки любого пользовательского ввода

    Args:
        data: Пользовательские данные

    Returns:
        Очищенные безопасные данные
    """
    return SecurityValidator.sanitize_html(data)

def validate_user_message(message: str, field_type: str = "general") -> tuple[bool, str]:
    """
    Комплексная валидация пользовательского сообщения

    Args:
        message: Сообщение от пользователя
        field_type: Тип поля (email, phone, general)

    Returns:
        (is_valid, error_message)
    """
    if not message:
        return False, "Поле обязательно для заполнения"

    # Базовая проверка длины
    is_valid, error = SecurityValidator.validate_message_length(message)
    if not is_valid:
        return False, error

    # Проверка на недопустимый контент
    is_valid, error = SecurityValidator.validate_content(message)
    if not is_valid:
        return False, error

    # Специфическая валидация для разных типов полей
    if field_type == "email":
        return SecurityValidator.validate_email_advanced(message)
    elif field_type == "phone":
        return SecurityValidator.validate_phone_advanced(message)

    return True, ""

# Логирование событий безопасности
def log_security_event(event_type: str, details: dict, severity: str = "warning"):
    """
    Логирование событий безопасности

    Args:
        event_type: Тип события (xss_attempt, spam_detected, etc.)
        details: Детали события
        severity: Уровень серьезности
    """
    log_data = {
        'event_type': event_type,
        'severity': severity,
        **details
    }

    if severity == "critical":
        logger.critical(f"Security event: {event_type}", extra=log_data)
    elif severity == "warning":
        logger.warning(f"Security event: {event_type}", extra=log_data)
    else:
        logger.info(f"Security event: {event_type}", extra=log_data)

# Конфигурация безопасности
SECURITY_CONFIG = {
    'MAX_MESSAGE_LENGTH': getattr(settings, 'AI_MAX_MESSAGE_LENGTH', 10000),
    'MIN_DESCRIPTION_LENGTH': getattr(settings, 'AI_MIN_DESCRIPTION_LENGTH', 200),
    'ENABLE_CONTENT_FILTERING': getattr(settings, 'AI_ENABLE_CONTENT_FILTERING', True),
    'ENABLE_SPAM_PROTECTION': getattr(settings, 'AI_ENABLE_SPAM_PROTECTION', True),
    'LOG_SECURITY_EVENTS': getattr(settings, 'AI_LOG_SECURITY_EVENTS', True),
}

logger.info("AI Consultant Security module loaded successfully")