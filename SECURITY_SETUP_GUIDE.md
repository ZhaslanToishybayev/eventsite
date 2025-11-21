# 🛡️ Руководство по настройке безопасности и мониторинга

## 📦 Установка зависимостей

```bash
# Установка дополнительных пакетов безопасности
pip install -r security_requirements.txt

# Для систем на Debian/Ubuntu:
sudo apt-get install libmagic1

# Для систем на CentOS/RHEL:
sudo yum install file-devel
```

## ⚙️ Настройка

### 1. Обновление settings.py

Настройки уже добавлены в `core/settings.py`:

```python
# Security middleware
MIDDLEWARE = [
    # ...
    'core.security.SecurityHeadersMiddleware',
    'core.monitoring.AIMonitoringMiddleware',
    # ...
]
```

### 2. Rate Limiting

В `ai_consultant/api/views.py` уже настроен rate limiting:

```python
@ratelimit(key='ip', rate='30/m', method='POST', block=True)
```

### 3. Безопасная загрузка файлов

Используйте новые валидаторы в моделях:

```python
from core.validators import secure_image_validator, secure_document_validator

class Club(models.Model):
    logo = models.ImageField(
        upload_to='club/logos',
        validators=[secure_image_validator]
    )
```

## 🔍 Мониторинг

### API эндпоинты мониторинга:

1. **Статистика AI** (только для админов):
   ```
   GET /api/v1/ai-monitoring-stats/
   ```

2. **Проверка здоровья системы** (только для админов):
   ```
   GET /api/v1/system-health-check/
   ```

### Метрики, которые отслеживаются:

- Количество запросов в час/день
- Время ответа
- Процент ошибок
- Потребление токенов API
- Топ пользователей и IP адресов
- Подозрительная активность

## 🚨 Алерты

Система автоматически детектирует и логирует:

- Более 100 запросов в день от одного IP
- Более 200 запросов в день от одного пользователя
- Время ответа более 30 секунд
- Процент ошибок более 50%
- Попытки SQL инъекций и XSS

## 📊 Логирование

Мониторинг использует стандартный логгер Django:

```python
import logging
logger = logging.getLogger(__name__)

# Алерты уровня WARNING для подозрительной активности
# Детальная информация уровня INFO для всех запросов
```

## 🛡️ Безопасность файлов

### Новые функции:

1. **Проверка MIME типов** с помощью python-magic
2. **Валидация расширений** файлов
3. **Проверка размеров** изображений
4. **Сканирование содержимого** на вредоносный код
5. **Генерация безопасных** имен файлов

### Пример использования:

```python
from core.validators import SecureFileUploadHandler

# Безопасная загрузка файла
handler = SecureFileUploadHandler()
safe_filename = handler.handle_upload(
    file_obj=request.FILES['avatar'],
    upload_path='avatars/',
    file_type='image',
    prefix='user_avatar'
)
```

## 🔒 CSP Заголовки

Добавлены Content Security Policy заголовки:

```javascript
// Разрешены домены:
- 'self' (ваш домен)
- https://kit.fontawesome.com
- https://fonts.googleapis.com
- https://www.google.com
- https://www.gstatic.com
```

## ⚡ Производительность

Рекомендации для PostgreSQL:

```sql
-- Индексы для частых запросов
CREATE INDEX CONCURRENTLY idx_club_members_count ON clubs_club(members_count DESC);
CREATE INDEX CONCURRENTLY idx_club_likes_count ON clubs_club(likes_count DESC);
CREATE INDEX CONCURRENTLY idx_chat_session_created ON ai_consultant_chatsession(created_at DESC);
```

## 🧪 Тестирование

Проверьте работу безопасности:

```bash
# Тест rate limiting
for i in {1..35}; do
    curl -X POST http://localhost:8000/api/v1/chat/ \
         -H "Content-Type: application/json" \
         -d '{"message": "test"}'
done

# Тест безопасности файлов
curl -X POST http://localhost:8000/upload/ \
     -F "file=@malicious.php"

# Тест XSS
curl -X POST http://localhost:8000/api/v1/chat/ \
     -H "Content-Type: application/json" \
     -d '{"message": "<script>alert(1)</script>"}'
```

## 📝 Не забудьте

1. **Установить зависимости** из `security_requirements.txt`
2. **Настроить logging** для мониторинга алертов
3. **Проверить работу** всех защитных механизмов
4. **Обновить индексы** базы данных
5. **Настроить мониторинг** production окружения

## 🔄 Для production

- Установить DEBUG=False
- Настроить HTTPS
- Настроить connection pooling для PostgreSQL
- Добавить системы мониторинга (Prometheus/Grafana)
- Настроить бэкапы логов