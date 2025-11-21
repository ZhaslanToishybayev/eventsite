import re
import html
import bleach
from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin
import logging

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware для добавления security заголовков
    """

    def process_response(self, request, response):
        # Content Security Policy
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://kit.fontawesome.com https://www.google.com https://www.gstatic.com https://cdn.jsdelivr.net",
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://ka-f.fontawesome.com",
            "font-src 'self' https://fonts.gstatic.com https://ka-f.fontawesome.com",
            "img-src 'self' data: https: http:",
            "connect-src 'self' https://api.openai.com https://ka-f.fontawesome.com https://cdn.jsdelivr.net",
            "frame-src 'none'",
            "object-src 'none'",
            "base-uri 'self'",
            "form-action 'self'",
            "upgrade-insecure-requests"
        ]

        if settings.DEBUG:
            # В режиме разработки разрешаем больше
            csp_directives[1] = "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://kit.fontawesome.com https://www.google.com https://www.gstatic.com https://cdn.jsdelivr.net 'unsafe-dynamic'"
            csp_directives[2] = "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://ka-f.fontawesome.com"
            csp_directives[5] = "connect-src 'self' https://api.openai.com https://ka-f.fontawesome.com https://cdn.jsdelivr.net"

        response['Content-Security-Policy'] = '; '.join(csp_directives)

        # Другие security заголовки
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'

        # HSTS (только для HTTPS)
        if not settings.DEBUG and request.is_secure():
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

        return response


class InputSanitizer:
    """
    Сервис для очистки и валидации входных данных
    """

    # Белый список разрешенных HTML тегов
    ALLOWED_HTML_TAGS = [
        'p', 'br', 'strong', 'em', 'u', 'ul', 'ol', 'li',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'blockquote', 'code', 'pre',
        'a', 'img'
    ]

    # Белый список разрешенных атрибутов
    ALLOWED_HTML_ATTRIBUTES = {
        'a': ['href', 'title', 'target'],
        'img': ['src', 'alt', 'width', 'height'],
        '*': ['class']
    }

    @staticmethod
    def sanitize_html(content, allowed_tags=None, allowed_attributes=None):
        """
        Очищает HTML контент с использованием bleach
        """
        try:
            if not content:
                return ''

            # Используем значения по умолчанию если не указаны
            tags = allowed_tags or InputSanitizer.ALLOWED_HTML_TAGS
            attributes = allowed_attributes or InputSanitizer.ALLOWED_HTML_ATTRIBUTES

            # Очищаем HTML
            clean_content = bleach.clean(
                content,
                tags=tags,
                attributes=attributes,
                strip=True
            )

            # Дополнительная очистка ссылок
            clean_content = InputSanitizer._sanitize_urls(clean_content)

            return clean_content

        except Exception as e:
            logger.error(f"Error sanitizing HTML: {e}")
            return ''  # Возвращаем пустую строку при ошибке

    @staticmethod
    def _sanitize_urls(content):
        """
        Дополнительная очистка URL
        """
        try:
            # Ищем все href и src атрибуты
            url_pattern = re.compile(r'(href|src)="([^"]*)"', re.IGNORECASE)

            def clean_url(match):
                attr_name = match.group(1).lower()
                url = match.group(2)

                # Проверяем безопасность URL
                if InputSanitizer._is_safe_url(url):
                    return match.group(0)
                else:
                    # Заменяем небезопасный URL на #
                    return f'{attr_name}="#"'

            return url_pattern.sub(clean_url, content)

        except Exception as e:
            logger.error(f"Error sanitizing URLs: {e}")
            return content

    @staticmethod
    def _is_safe_url(url):
        """
        Проверяет безопасность URL
        """
        try:
            # Пропускаем пустые и якорные ссылки
            if not url or url == '#' or url.startswith('mailto:'):
                return True

            # Разрешенные протоколы
            allowed_protocols = ['http', 'https', 'mailto', 'tel']

            # Проверяем протокол
            if '://' in url:
                protocol = url.split('://')[0].lower()
                if protocol not in allowed_protocols:
                    return False

            # Проверяем на javascript: и другие опасные протоколы
            dangerous_patterns = [
                'javascript:', 'data:', 'vbscript:', 'file:',
                'ftp:', 'irc:', 'telnet:'
            ]

            url_lower = url.lower()
            for pattern in dangerous_patterns:
                if url_lower.startswith(pattern):
                    return False

            return True

        except Exception:
            return False

    @staticmethod
    def sanitize_text(text):
        """
        Базовая очистка текста
        """
        if not text:
            return ''

        # HTML экранирование
        sanitized = html.escape(str(text))

        # Дополнительная очистка от потенциально опасных символов
        sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', sanitized)

        return sanitized

    @staticmethod
    def validate_field(value, field_type='text', max_length=None, min_length=None):
        """
        Валидация поля с определенными правилами
        """
        try:
            if value is None:
                return None

            # Преобразуем в строку
            value = str(value).strip()

            # Проверяем длину
            if max_length and len(value) > max_length:
                raise ValidationError(f'Поле превышает максимальную длину {max_length} символов')

            if min_length and len(value) < min_length:
                raise ValidationError(f'Поле должно содержать минимум {min_length} символов')

            # Проверяем на пустоту
            if not value and min_length and min_length > 0:
                raise ValidationError('Поле не может быть пустым')

            # Дополнительная валидация в зависимости от типа
            if field_type == 'email':
                if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
                    raise ValidationError('Некорректный email адрес')

            elif field_type == 'phone':
                # Упрощенная валидация телефона
                if not re.match(r'^\+?[\d\s\-\(\)]+$', value):
                    raise ValidationError('Некорректный номер телефона')

            elif field_type == 'url':
                if not InputSanitizer._is_safe_url(value):
                    raise ValidationError('Некорректный URL')

            return value

        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error validating field: {e}")
            raise ValidationError('Ошибка валидации поля')


class SecurityValidator:
    """
    Комплексная проверка безопасности
    """

    @staticmethod
    def check_sql_injection(input_string):
        """
        Проверка на SQL инъекции
        """
        if not input_string:
            return False

        sql_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|SCRIPT)\b)",
            r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
            r"(--|#|/\*|\*/)",
            r"(\b(DECLARE|CAST|CONVERT)\b)",
            r"(\b(SHOw|DESCRIBE|EXPLAIN)\b)"
        ]

        input_lower = input_string.lower()
        for pattern in sql_patterns:
            if re.search(pattern, input_lower):
                logger.warning(f"Potential SQL injection detected: {input_string[:100]}...")
                return True

        return False

    @staticmethod
    def check_xss(input_string):
        """
        Проверка на XSS атаки
        """
        if not input_string:
            return False

        xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"vbscript:",
            r"onload\s*=",
            r"onerror\s*=",
            r"onclick\s*=",
            r"onmouseover\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>",
            r"<link[^>]*>",
            r"<meta[^>]*>",
            r"eval\s*\(",
            r"alert\s*\(",
            r"document\.(cookie|location|write)"
        ]

        input_lower = input_string.lower()
        for pattern in xss_patterns:
            if re.search(pattern, input_lower):
                logger.warning(f"Potential XSS detected: {input_string[:100]}...")
                return True

        return False

    @staticmethod
    def validate_input(input_string, field_name='field'):
        """
        Комплексная валидация входных данных
        """
        if not input_string:
            return True

        # Проверка на SQL инъекции
        if SecurityValidator.check_sql_injection(input_string):
            raise ValidationError(f'Обнаружена попытка SQL инъекции в поле {field_name}')

        # Проверка на XSS
        if SecurityValidator.check_xss(input_string):
            raise ValidationError(f'Обнаружена попытка XSS атаки в поле {field_name}')

        return True


def sanitize_input_data(request_data):
    """
    Очистка всех входных данных запроса
    """
    try:
        sanitized_data = {}

        for key, value in request_data.items():
            if isinstance(value, str):
                # Проверяем безопасность
                SecurityValidator.validate_input(value, key)

                # Очищаем HTML если это разрешено
                if key in ['content', 'description', 'message']:
                    sanitized_data[key] = InputSanitizer.sanitize_html(value)
                else:
                    sanitized_data[key] = InputSanitizer.sanitize_text(value)
            else:
                sanitized_data[key] = value

        return sanitized_data

    except Exception as e:
        logger.error(f"Error sanitizing input data: {e}")
        raise ValidationError('Ошибка очистки входных данных')