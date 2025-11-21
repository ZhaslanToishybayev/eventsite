from django.core.exceptions import ValidationError


def max_image_size_1MB(value):
    limit = 1 * 1024 * 1024
    if value.size > limit:
        raise ValidationError('Файл очень большой. Размер не должен превышать 1 МБ.')
