#!/bin/bash

# 🚀 Manual Production Setup for UnitySphere
# Ручная настройка production без sudo прав

echo "🚀 Manual Production Setup for UnitySphere"
echo "========================================="
echo ""

cd /var/www/myapp/eventsite

# 1. Проверка виртуального окружения
echo "1. Проверка виртуального окружения..."
if [ -d "venv" ]; then
    echo "✅ Виртуальное окружение найдено"
    source venv/bin/activate
    echo "✅ Виртуальное окружение активировано"
else
    echo "❌ Виртуальное okружение не найдено"
    exit 1
fi

# 2. Проверка Django
echo ""
echo "2. Проверка Django..."
if python -c "import django; print('Django version:', django.get_version())" 2>/dev/null; then
    echo "✅ Django установлен"
else
    echo "❌ Django not installed"
    exit 1
fi

# 3. Проверка зависимостей
echo ""
echo "3. Проверка AI зависимостей..."
if python -c "import openai; print('OpenAI library available')" 2>/dev/null; then
    echo "✅ OpenAI library available"
else
    echo "⚠️  OpenAI library not found, installing..."
    pip install openai
fi

# 4. Запуск Django сервера
echo ""
echo "4. Запуск Django сервера на порту 8001..."
echo "   Адрес: http://127.0.0.1:8001"

# Остановим предыдущие процессы
pkill -f "python.*runserver" 2>/dev/null || true
sleep 2

# Запустим Django сервер
nohup python manage.py runserver 127.0.0.1:8001 --insecure > django_server.log 2>&1 &
DJANGO_PID=$!

echo "✅ Django сервер запущен (PID: $DJANGO_PID)"

# 5. Проверка запуска
sleep 5
if curl -s http://127.0.0.1:8001/ > /dev/null; then
    echo "✅ Django сервер отвечает"
else
    echo "❌ Django сервер не отвечает"
    echo "Проверка логов: tail -f django_server.log"
    exit 1
fi

# 6. Проверка AI API
echo ""
echo "5. Проверка AI API..."
if curl -s http://127.0.0.1:8001/api/v1/ai/health/ > /dev/null; then
    echo "✅ AI API доступен"
else
    echo "⚠️  AI API недоступен, но Django работает"
fi

# 7. Создание nginx конфигурации (без установки)
echo ""
echo "6. Создание nginx конфигурации..."
cat > nginx_manual_config.conf << 'EOF'
# Manual nginx configuration for UnitySphere
# Copy this to /etc/nginx/sites-available/unitysphere if you have sudo access

server {
    listen 80;
    server_name fan-club.kz www.fan-club.kz;

    # Logging
    access_log /var/log/nginx/unitysphere_access.log;
    error_log /var/log/nginx/unitysphere_error.log;

    # Health check
    location /health/ {
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }

    # Static files
    location /static/ {
        alias /var/www/myapp/eventsite/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /var/www/myapp/eventsite/media/;
        expires 1y;
        add_header Cache-Control "public";
    }

    # API endpoints
    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Main application
    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

echo "✅ Nginx конфигурация создана: nginx_manual_config.conf"

# 8. Инструкции для nginx
echo ""
echo "📋 Инструкции для nginx (требуются sudo права):"
echo ""
echo "1. Скопируйте конфигурацию:"
echo "   sudo cp nginx_manual_config.conf /etc/nginx/sites-available/unitysphere"
echo ""
echo "2. Активируйте сайт:"
echo "   sudo ln -sf /etc/nginx/sites-available/unitysphere /etc/nginx/sites-enabled/"
echo "   sudo rm -f /etc/nginx/sites-enabled/default"
echo ""
echo "3. Проверьте конфигурацию:"
echo "   sudo nginx -t"
echo ""
echo "4. Перезапустите nginx:"
echo "   sudo systemctl restart nginx"
echo ""

# 9. Финальная информация
echo "🎉 Manual Setup Completed!"
echo "=========================="
echo ""
echo "🔗 Django сервер работает по адресу:"
echo "   http://127.0.0.1:8001"
echo ""
echo "📂 Логи Django:"
echo "   tail -f django_server.log"
echo ""
echo "🚫 Для доступа через nginx и домен fan-club.kz:"
echo "   Необходимо настроить nginx с sudo правами (см. инструкции выше)"
echo ""
echo "✅ Production setup completed!"