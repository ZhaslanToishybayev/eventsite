# 🚀 Инструкция по настройке Production для UnitySphere

## 📋 Подготовка сервера

### Системные требования
- **ОС:** Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **RAM:** 4GB+ (рекомендуется 8GB)
- **CPU:** 2+ ядра (рекомендуется 4+)
- **Storage:** 50GB+ SSD

### Установка зависимостей

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка необходимых пакетов
sudo apt install -y python3 python3-pip python3-venv python3-dev
sudo apt install -y postgresql postgresql-contrib postgresql-client
sudo apt install -y redis-server nginx
sudo apt install -y build-essential libpq-dev
sudo apt install -y supervisor git curl wget
sudo apt install -y libmagic1 libmagic-dev  # для безопасности файлов
```

## 🗄️ Настройка PostgreSQL

### Создание базы данных
```bash
# Переключение на пользователя postgres
sudo -i -u postgres

# Создание пользователя и базы данных
createuser --interactive unitysphere_user
createdb -O unitysphere_user unitysphere_prod

# Установка пароля
psql -c "ALTER USER unitysphere_user PASSWORD 'your_secure_password';"

# Выход из postgres
exit
```

### Оптимизация PostgreSQL
```bash
# Редактирование конфигурации
sudo nano /etc/postgresql/13/main/postgresql.conf

# Добавить/изменить параметры:
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
max_connections = 100
shared_preload_libraries = 'pg_stat_statements'
```

## 📦 Настройка Redis
```bash
# Конфигурация Redis
sudo nano /etc/redis/redis.conf

# Установить параметры:
maxmemory 256mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000

# Перезапуск Redis
sudo systemctl restart redis
sudo systemctl enable redis
```

## 🔧 Настройка проекта

### Развертывание кода
```bash
# Создание директории проекта
sudo mkdir -p /var/www/unitysphere
sudo chown www-data:www-data /var/www/unitysphere

# Клонирование репозитория
sudo -u www-data git clone https://github.com/your-username/unitysphere.git /var/www/unitysphere
cd /var/www/unitysphere

# Создание виртуального окружения
sudo -u www-data python3 -m venv /var/www/venv_unitysphere
sudo -u www-data /var/www/venv_unitysphere/bin/pip install --upgrade pip
```

### Установка зависимостей
```bash
# Активация виртуального окружения
source /var/www/venv_unitysphere/bin/activate

# Установка зависимостей
pip install -r requirements_production.txt
```

### Настройка .env файла
```bash
# Создание .env файла
sudo -u www-data nano /var/www/unitysphere/.env

# Содержимое .env:
DJANGO_SECRET_KEY=your-very-secure-secret-key-here
DEBUG=False
ALLOWED_HOSTS=fan-club.kz,www.fan-club.kz

# Database
POSTGRES_NAME=unitysphere_prod
POSTGRES_USER=unitysphere_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Email (опционально)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# OpenAI
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4o-mini

# Sentry (опционально)
SENTRY_DSN=your-sentry-dsn
```

## 🚀 Деплой приложения

### Миграции и сбор статики
```bash
cd /var/www/unitysphere
source /var/www/venv_unitysphere/bin/activate

# Миграции базы данных
python manage.py migrate --settings=core.settings_production

# Создание суперпользователя
python manage.py createsuperuser --settings=core.settings_production

# Сбор статических файлов
python manage.py collectstatic --settings=core.settings_production --noinput

# Применение PostgreSQL оптимизаций
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings_production')
django.setup()
from core.migrations_postgresql import *
print('PostgreSQL optimizations applied')
"
```

## 🔧 Настройка системных сервисов

### Gunicorn сервис
```bash
# Копирование файла сервиса
sudo cp systemd/unitysphere.service /etc/systemd/system/

# Перезагрузка systemd
sudo systemctl daemon-reload

# Включение и запуск сервиса
sudo systemctl enable unitysphere
sudo systemctl start unitysphere

# Проверка статуса
sudo systemctl status unitysphere
```

### Nginx конфигурация
```bash
# Копирование конфигурации
sudo cp nginx/unitysphere.conf /etc/nginx/sites-available/

# Создание символической ссылки
sudo ln -s /etc/nginx/sites-available/unitysphere.conf /etc/nginx/sites-enabled/

# Удаление стандартного сайта
sudo rm /etc/nginx/sites-enabled/default

# Тестирование конфигурации
sudo nginx -t

# Перезапуск Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### Создание лог директорий
```bash
sudo mkdir -p /var/log/unitysphere
sudo chown www-data:www-data /var/log/unitysphere

# Директория для бэкапов
sudo mkdir -p /var/backups/unitysphere
sudo chown www-data:www-data /var/backups/unitysphere
```

## 🔒 SSL Сертификат (Let's Encrypt)

### Установка Certbot
```bash
sudo apt install certbot python3-certbot-nginx

# Получение сертификата
sudo certbot --nginx -d fan-club.kz -d www.fan-club.kz

# Автоматическое обновление
sudo crontab -e
# Добавить строку:
0 12 * * * /usr/bin/certbot renew --quiet
```

## 🔍 Тестирование и проверка

### Проверка работы приложения
```bash
# Проверка здоровья системы
curl http://localhost/api/v1/system-health-check/

# Проверка статической страницы
curl http://localhost/

# Проверка API
curl -X POST http://localhost/api/v1/chat/ \
     -H "Content-Type: application/json" \
     -d '{"message": "test message"}'
```

### Проверка логов
```bash
# Логи Gunicorn
sudo journalctl -u unitysphere -f

# Логи Nginx
sudo tail -f /var/log/nginx/unitysphere_access.log
sudo tail -f /var/log/nginx/unitysphere_error.log

# Логи Django
sudo tail -f /var/log/unitysphere/django.log
```

## 🔄 Деплой с использованием скрипта

### Использование деплой скрипта
```bash
# Сделать скрипт исполняемым
chmod +x deploy.sh

# Деплой на production
sudo ./deploy.sh production

# Деплой на staging
sudo ./deploy.sh staging

# Откат изменений
sudo ./deploy.sh rollback
```

## 📊 Мониторинг

### Настройка мониторинга
```bash
# Добавление в crontab для регулярного мониторинга
sudo crontab -e

# Добавить задачи мониторинга:
# Проверка здоровья системы каждые 5 минут
*/5 * * * * curl -sf http://localhost/api/v1/system-health-check/ || /usr/bin/systemctl restart unitysphere

# Очистка старых логов каждое утро
0 6 * * * find /var/log/unitysphere -name "*.log" -mtime +30 -delete

# Бэкап базы данных каждый день в 2 часа ночи
0 2 * * * /usr/bin/pg_dump -h localhost -U unitysphere_user unitysphere_prod | gzip > /var/backups/unitysphere/db_$(date +\%Y\%m\%d).sql.gz
```

## 🔧 Оптимизация производительности

### Настройка connection pooling
```bash
# В settings_production уже настроен connection pooling
# Дополнительные параметры можно настроить в PostgreSQL:

# sudo nano /etc/postgresql/13/main/postgresql.conf
# max_connections = 100
# shared_buffers = 256MB
# work_mem = 4MB
# maintenance_work_mem = 64MB
```

### Кэширование Redis
```bash
# Проверка работы Redis
redis-cli ping
redis-cli info memory

# Прогрев кэша
cd /var/www/unitysphere
source /var/www/venv_unitysphere/bin/activate
python manage.py shell -c "
from core.cache import cache_warmer
cache_warmer.warm_all()
print('Cache warmed successfully')
"
```

## 🚨 Решение проблем

### Частые проблемы и решения:

1. **Gunicorn не запускается**
   ```bash
   # Проверка логов
   sudo journalctl -u unitysphere -n 50

   # Проверка прав доступа
   sudo chown -R www-data:www-data /var/www/unitysphere
   ```

2. **Ошибка подключения к базе данных**
   ```bash
   # Проверка статуса PostgreSQL
   sudo systemctl status postgresql

   # Проверка подключения
   psql -h localhost -U unitysphere_user -d unitysphere_prod
   ```

3. **Ошибка статических файлов**
   ```bash
   # Пересборка статики
   python manage.py collectstatic --settings=core.settings_production --noinput

   # Проверка прав доступа
   sudo chown -R www-data:www-data /var/www/unitysphere/static
   ```

4. **Redis не доступен**
   ```bash
   # Проверка статуса Redis
   sudo systemctl status redis

   # Тест подключения
   redis-cli ping
   ```

## ✅ Завершение настройки

После выполнения всех шагов:

1. **Проверьте работу сайта** через браузер
2. **Проверьте HTTPS редирект**
3. **Протестируйте AI консультант**
4. **Проверьте загрузку файлов**
5. **Убедитесь что мониторинг работает**

Ваш UnitySphere готов к production использованию! 🎉