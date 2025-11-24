# UnitySphere - fan-club.kz Production Setup Guide

## 🚀 Быстрый старт

### 1. Запуск сайта

```bash
cd /var/www/myapp/eventsite
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

### 2. Доступ к сайту

- **Локально**: http://localhost:8000
- **По IP**: http://77.243.80.110:8000
- **Админка**: http://localhost:8000/admin/

### 3. Создание суперпользователя

```bash
python manage.py createsuperuser
```

## 📋 Настройка для Production

### 1. Nginx конфигурация

Скопируйте конфигурацию из `/var/www/myapp/eventsite/nginx_fan-club.kz` в `/etc/nginx/sites-available/fan-club.kz`:

```bash
sudo cp /var/www/myapp/eventsite/nginx_fan-club.kz /etc/nginx/sites-available/fan-club.kz
sudo ln -s /etc/nginx/sites-available/fan-club.kz /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 2. Systemd сервис

Скопируйте сервис из `/var/www/myapp/eventsite/unitysphere.service` в `/etc/systemd/system/`:

```bash
sudo cp /var/www/myapp/eventsite/unitysphere.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable unitysphere
sudo systemctl start unitysphere
```

### 3. SSL сертификаты (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d fan-club.kz -d www.fan-club.kz
```

## 🔧 Настройка базы данных

### SQLite (Development)
По умолчанию используется SQLite. Файл базы данных: `db.sqlite3`

### PostgreSQL (Production)

1. Установите PostgreSQL:
```bash
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

2. Создайте базу данных:
```bash
sudo -u postgres psql <<EOF
CREATE DATABASE unitysphere_prod;
CREATE USER unitysphere_user WITH PASSWORD 'unitysphere123';
GRANT ALL PRIVILEGES ON DATABASE unitysphere_prod TO unitysphere_user;
EOF
```

3. Обновите `.env` файл:
```
DB_NAME=unitysphere_prod
DB_USER=unitysphere_user
DB_PASSWORD=unitysphere123
DB_HOST=localhost
DB_PORT=5432
```

## 🤖 ИИ-консультант

### Требования
- OpenAI API ключ
- Anthropic API ключ
- Sentence Transformers
- ChromaDB

### Настройка
1. Установите AI зависимости:
```bash
pip install openai anthropic chromadb sentence-transformers
```

2. Обновите `.env` файл:
```
AI_CONSULTANT_ENABLED=True
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
```

## 🔐 Переменные окружения

Обязательные переменные в `.env` файле:

```env
# Django
DJANGO_SECRET_KEY=your-secret-key
DEBUG=False

# Database
DB_NAME=your-db-name
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432

# AI
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
AI_CONSULTANT_ENABLED=True

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email
EMAIL_HOST_PASSWORD=your-password

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

## 🚨 Важные моменты

1. **Безопасность**: Не используйте DEBUG=True в production
2. **SSL**: Настройте HTTPS с помощью Let's Encrypt
3. **Бэкапы**: Регулярно делайте бэкапы базы данных
4. **Мониторинг**: Настройте мониторинг сервера
5. **API ключи**: Храните API ключи в безопасном месте

## 🐛 Решение проблем

### Django не запускается
```bash
source venv/bin/activate
pip install -r requirements.txt
python manage.py check
```

### Nginx не видит сайт
```bash
sudo nginx -t
sudo systemctl restart nginx
```

### Ошибки базы данных
```bash
python manage.py migrate
python manage.py makemigrations
```

## 📞 Поддержка

Если возникнут проблемы:
1. Проверьте логи: `tail -f /var/log/nginx/*.log`
2. Проверьте Django логи: `python manage.py runserver`
3. Проверьте системные логи: `journalctl -u unitysphere`

---

**Готово!** Ваш сайт fan-club.kz now должен работать полноценно! 🎉