# 🔧 ИСПРАВЛЕНИЕ CSRF_TRUSTED_ORIGINS

Проблема найдена! Django настроен на HTTPS в CSRF_TRUSTED_ORIGINS, но сайт работает по HTTP.

## Решение:

### Вариант 1: Добавить HTTP в CSRF_TRUSTED_ORIGINS
```python
# В файле /var/www/myapp/eventsite/core/settings.py
CSRF_TRUSTED_ORIGINS = [
    'https://fan-club.kz',
    'https://www.fan-club.kz',
    'http://fan-club.kz',
    'http://www.fan-club.kz'
]
```

### Вариант 2: Отключить CSRF_TRUSTED_ORIGINS (временно для тестирования)
```python
# В файле /var/www/myapp/eventsite/core/settings.py
CSRF_TRUSTED_ORIGINS = []
```

### Вариант 3: Настроить HTTPS (рекомендуется)
Настроить SSL сертификаты и перенаправлять HTTP на HTTPS.

## Команды для исправления:

```bash
# Отредактировать settings.py
sudo nano /var/www/myapp/eventsite/core/settings.py

# Найти строку CSRF_TRUSTED_ORIGINS и исправить:
CSRF_TRUSTED_ORIGINS = ['http://fan-club.kz', 'http://www.fan-club.kz']

# Перезапустить Django
sudo systemctl restart nginx
# И перезапустить Django процессы
```

## Проверка:
После исправления проверьте:
```bash
curl -I http://fan-club.kz
```