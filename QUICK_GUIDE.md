# Краткая инструкция по использованию UnitySphere

## Доступ к сайту:

### Вариант 1: HTTP (рекомендуется)
```
http://fan-club.kz:8000/
```

### Вариант 2: HTTPS (с самоподписанным сертификатом)
```
https://fan-club.kz:8443/
```
*В браузере может появиться предупреждение о безопасности - нажмите "Продолжить"*

## AI Консультант:

### Эндпоинты Actionable AI:
1. **Статус системы**: `/api/v1/actionable/status/`
2. **Чат с AI**: `/api/v1/actionable/chat/`

### Тест SSL соединения:
```
http://fan-club.kz:8000/ssl_test.html
```

## Команды управления:

### Проверка запущенных процессов:
```bash
ps aux | grep python
```

### Проверка портов:
```bash
netstat -tuln | grep -E '8000|8443'
```

### Перезапуск Django:
```bash
# Остановить
pkill -f runserver
pkill -f runsslserver

# Запустить HTTP
source venv/bin/activate && python manage.py runserver 0.0.0.0:8000

# Запустить HTTPS
source venv/bin/activate && python manage.py runsslserver --certificate cert.pem --key key.pem 0.0.0.0:8443
```

## Важно:
- Сервер работает стабильно, память не перегружена (2GB RAM)
- Используется Actionable AI v3.0
- Django работает через runserver (не gunicorn)
- SSL настроен через django-sslserver