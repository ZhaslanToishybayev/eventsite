#!/bin/bash

# Production Setup Script for UnitySphere (fan-club.kz)

echo "🚀 Начинаем настройку production окружения..."

# 1. Установка PostgreSQL
echo "📦 Устанавливаем PostgreSQL..."
sudo apt update
sudo apt install postgresql postgresql-contrib -y

# 2. Запуск PostgreSQL
echo "🔄 Запускаем PostgreSQL..."
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 3. Создание базы данных и пользователя
echo "🗄️ Создаем базу данных..."
sudo -u postgres psql <<EOF
CREATE DATABASE unitysphere_prod;
CREATE USER unitysphere_user WITH PASSWORD 'unitysphere123';
ALTER ROLE unitysphere_user SET client_encoding TO 'utf8';
ALTER ROLE unitysphere_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE unitysphere_user SET timezone TO 'Asia/Almaty';
GRANT ALL PRIVILEGES ON DATABASE unitysphere_prod TO unitysphere_user;
EOF

# 4. Установка Python зависимостей
echo "🐍 Устанавливаем Python зависимости..."
cd /var/www/myapp/eventsite
pip3 install -r requirements.txt
pip3 install -r requirements.production.txt

# 5. Создание .env файла
echo "⚙️ Создаем .env файл..."
cat > .env <<EOF
# Django Settings
DJANGO_SECRET_KEY='your-secret-key-here-change-in-production'
DEBUG=False

# Database Settings
POSTGRES_NAME=unitysphere_prod
POSTGRES_USER=unitysphere_user
POSTGRES_PASSWORD=unitysphere123
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Redis Settings (если используется)
REDIS_HOST=localhost
REDIS_PORT=6379

# AI Settings
OPENAI_API_KEY=your-openai-api-key
SERENA_ENABLED=True
SERENA_URL=http://localhost:8001
SERENA_TIMEOUT=30
AI_CONSULTANT_ENABLED=True

# Email Settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@fan-club.kz

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Anthropic AI
ANTHROPIC_API_KEY=your-anthropic-api-key
EOF

# 6. Настройка базы данных
echo "🗄️ Настраиваем базу данных..."
python3 manage.py migrate
python3 manage.py collectstatic --noinput

# 7. Создание суперпользователя
echo "👤 Создаем суперпользователя..."
echo "Введите имя пользователя для суперпользователя:"
read username
echo "Введите email:"
read email
python3 manage.py createsuperuser --username $username --email $email

echo "✅ Настройка завершена!"

echo "📋 Следующие шаги:"
echo "1. Настройте Nginx конфигурацию для fan-club.kz"
echo "2. Настройте SSL сертификаты (Let's Encrypt)"
echo "3. Запустите ИИ-серверы"
echo "4. Настройте systemd сервисы для Django"