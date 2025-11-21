import magic
import os
import hashlib
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Белые списки разрешенных типов
ALLOWED_IMAGE_TYPES = {
    'image/jpeg': ['jpg', 'jpeg'],
    'image/png': ['png'],
    'image/gif': ['gif'],
    'image/webp': ['webp']
}

ALLOWED_DOCUMENT_TYPES = {
    'application/pdf': ['pdf'],
    'application/msword': ['doc'],
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['docx'],
    'text/plain': ['txt']
}

# Максимальные размеры файлов (в байтах)
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_DOCUMENT_SIZE = 10 * 1024 * 1024  # 10MB

# Максимальные размеры изображений
MAX_IMAGE_WIDTH = 4000
MAX_IMAGE_HEIGHT = 4000


class SecureFileValidator:
    """
    Безопасная валидация загружаемых файлов
    """

    @staticmethod
    def validate_file_type(file_obj, allowed_types_dict):
        """
        Проверяет MIME тип файла с помощью python-magic
        """
        try:
            # Читаем первые 2048 байт для определения типа
            file_obj.seek(0)
            file_content = file_obj.read(2048)
            file_obj.seek(0)

            # Определяем MIME тип
            mime_type = magic.from_buffer(file_content, mime=True)

            if mime_type not in allowed_types_dict:
                raise ValidationError(
                    f'Недопустимый тип файла: {mime_type}. '
                    f'Разрешенные типы: {", ".join(allowed_types_dict.keys())}'
                )

            return mime_type

        except Exception as e:
            logger.error(f"Error validating file type: {e}")
            raise ValidationError('Не удалось определить тип файла')

    @staticmethod
    def validate_file_extension(file_obj, mime_type, allowed_types_dict):
        """
        Проверяет соответствие расширения файла MIME типу
        """
        filename = file_obj.name.lower()
        if not filename:
            raise ValidationError('Файл должен иметь имя')

        extension = filename.split('.')[-1]
        allowed_extensions = allowed_types_dict.get(mime_type, [])

        if extension not in allowed_extensions:
            raise ValidationError(
                f'Расширение .{extension} не соответствует типу файла {mime_type}. '
                f'Разрешенные расширения: {", ".join(allowed_extensions)}'
            )

    @staticmethod
    def validate_file_size(file_obj, max_size):
        """
        Проверяет размер файла
        """
        if file_obj.size > max_size:
            max_size_mb = max_size / (1024 * 1024)
            raise ValidationError(
                f'Размер файла превышает {max_size_mb:.1f}MB. '
                f'Текущий размер: {file_obj.size / (1024 * 1024):.1f}MB'
            )

    @staticmethod
    def validate_image_dimensions(file_obj):
        """
        Проверяет размеры изображения
        """
        try:
            width, height = get_image_dimensions(file_obj)
            if width > MAX_IMAGE_WIDTH or height > MAX_IMAGE_HEIGHT:
                raise ValidationError(
                    f'Разрешение изображения слишком большое. '
                    f'Максимальное разрешение: {MAX_IMAGE_WIDTH}x{MAX_IMAGE_HEIGHT}'
                )
        except Exception as e:
            logger.error(f"Error validating image dimensions: {e}")
            # Не блокируем загрузку если не удалось определить размеры

    @staticmethod
    def generate_safe_filename(original_filename, prefix=''):
        """
        Генерирует безопасное имя файла
        """
        # Получаем расширение
        extension = original_filename.split('.')[-1].lower() if '.' in original_filename else ''

        # Генерируем уникальное имя
        hash_obj = hashlib.sha256()
        hash_obj.update(os.urandom(32))
        unique_name = hash_obj.hexdigest()[:16]

        if prefix:
            safe_name = f"{prefix}_{unique_name}.{extension}"
        else:
            safe_name = f"{unique_name}.{extension}"

        return safe_name

    @staticmethod
    def scan_file_content(file_obj):
        """
        Базовая проверка содержимого файла на вредоносный код
        """
        try:
            file_obj.seek(0)
            content = file_obj.read(1024)  # Читаем первые 1KB
            file_obj.seek(0)

            # Проверяем на признаки вредоносного кода
            suspicious_patterns = [
                b'<?php',
                b'<script',
                b'javascript:',
                b'vbscript:',
                b'data:text/html',
                b'eval(',
                b'exec(',
                b'system(',
                b'shell_exec('
            ]

            content_lower = content.lower()
            for pattern in suspicious_patterns:
                if pattern in content_lower:
                    logger.warning(f"Suspicious pattern found in file: {pattern}")
                    raise ValidationError('Файл содержит потенциально опасный контент')

        except Exception as e:
            logger.error(f"Error scanning file content: {e}")
            # Не блокируем загрузку при ошибке сканирования


def secure_image_validator(file_obj):
    """
    Комплексная валидация изображений
    """
    # Проверяем размер
    SecureFileValidator.validate_file_size(file_obj, MAX_IMAGE_SIZE)

    # Проверяем MIME тип
    mime_type = SecureFileValidator.validate_file_type(file_obj, ALLOWED_IMAGE_TYPES)

    # Проверяем соответствие расширения
    SecureFileValidator.validate_file_extension(file_obj, mime_type, ALLOWED_IMAGE_TYPES)

    # Проверяем размеры изображения
    SecureFileValidator.validate_image_dimensions(file_obj)

    # Сканируем содержимое
    SecureFileValidator.scan_file_content(file_obj)

    return True


def secure_document_validator(file_obj):
    """
    Комплексная валидация документов
    """
    # Проверяем размер
    SecureFileValidator.validate_file_size(file_obj, MAX_DOCUMENT_SIZE)

    # Проверяем MIME тип
    mime_type = SecureFileValidator.validate_file_type(file_obj, ALLOWED_DOCUMENT_TYPES)

    # Проверяем соответствие расширения
    SecureFileValidator.validate_file_extension(file_obj, mime_type, ALLOWED_DOCUMENT_TYPES)

    # Сканируем содержимое
    SecureFileValidator.scan_file_content(file_obj)

    return True


class SecureFileUploadHandler:
    """
    Обработчик безопасной загрузки файлов с изоляцией
    """

    @staticmethod
    def handle_upload(file_obj, upload_path, file_type='image', prefix=''):
        """
        Обрабатывает загрузку файла с безопасностью
        """
        try:
            # Выбираем валидатор
            if file_type == 'image':
                secure_image_validator(file_obj)
            elif file_type == 'document':
                secure_document_validator(file_obj)
            else:
                raise ValueError(f'Unsupported file type: {file_type}')

            # Генерируем безопасное имя файла
            original_filename = file_obj.name
            safe_filename = SecureFileValidator.generate_safe_filename(original_filename, prefix)

            # Формируем полный путь
            full_path = os.path.join(upload_path, safe_filename)

            # Убедимся, что директория существует
            os.makedirs(upload_path, exist_ok=True)

            # Сохраняем файл
            with open(full_path, 'wb+') as destination:
                for chunk in file_obj.chunks():
                    destination.write(chunk)

            logger.info(f"File uploaded successfully: {full_path}")
            return safe_filename

        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            raise ValidationError(f'Ошибка загрузки файла: {str(e)}')


# Требуется установка: pip install python-magic