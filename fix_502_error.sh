#!/bin/bash

# 🚀 Быстрое восстановление сайта после 502 Bad Gateway
echo "🚀 ВОССТАНОВЛЕНИЕ САЙТА ПОСЛЕ 502 Bad Gateway"
echo "=============================================="

# Проверяем, работает ли Django сервер
echo "1. Проверка Django сервера..."
if curl -s http://localhost:8000/api/v1/ai/simplified/interactive/status/ > /dev/null; then
    echo "✅ Django сервер работает на порту 8000"
else
    echo "❌ Django сервер не работает, запускаем..."
    source venv/bin/activate && python manage.py runserver 0.0.0.0:8000 > /dev/null 2>&1 &
    sleep 3
    if curl -s http://localhost:8000/api/v1/ai/simplified/interactive/status/ > /dev/null; then
        echo "✅ Django сервер запущен"
    else
        echo "❌ Django сервер не запустился"
        exit 1
    fi
fi

# Создаем временную nginx конфигурацию без SSL
echo ""
echo "2. Создание временной nginx конфигурации..."
cat > /tmp/nginx_temp_config << 'EOF'
# Временная конфигурация nginx без SSL
server {
    listen 80;
    server_name fan-club.kz www.fan-club.kz;

    # Основное приложение
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Статические файлы
    location /static/ {
        alias /var/www/myapp/eventsite/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Медиа файлы
    location /media/ {
        alias /var/www/myapp/eventsite/media/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Проверка работоспособности
    location /health/ {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF

echo "✅ Временная конфигурация создана"

# Пробуем перезагрузить nginx с новой конфигурацией
echo ""
echo "3. Перезагрузка nginx..."
if command -v sudo >/dev/null 2>&1; then
    echo "Используем sudo для перезагрузки nginx..."
    if sudo cp /tmp/nginx_temp_config /etc/nginx/sites-available/fan-club.kz; then
        if sudo nginx -s reload; then
            echo "✅ Nginx перезагружен с новой конфигурацией"
        else
            echo "❌ Ошибка перезагрузки nginx"
            echo "Попробуем остановить и запустить nginx..."
            sudo systemctl stop nginx
            sleep 2
            sudo nginx
            if [ $? -eq 0 ]; then
                echo "✅ Nginx запущен"
            else
                echo "❌ Nginx не запустился"
                exit 1
            fi
        fi
    else
        echo "❌ Не удалось скопировать конфигурацию nginx"
        exit 1
    fi
else
    echo "⚠️ sudo не доступен, nginx останется в текущем состоянии"
    echo "Пожалуйста, перезагрузите nginx вручную:"
    echo "sudo cp /tmp/nginx_temp_config /etc/nginx/sites-available/fan-club.kz"
    echo "sudo nginx -s reload"
fi

# Проверяем доступность сайта
echo ""
echo "4. Проверка доступности сайта..."
sleep 3

if curl -s http://fan-club.kz/health/ | grep -q "healthy"; then
    echo "✅ Сайт доступен через nginx"
    echo "🌐 Проверка главной страницы..."
    if curl -s http://fan-club.kz/ | grep -q "Центр сообществ"; then
        echo "✅ Главная страница загружается"
        echo "💬 Проверка AI виджета..."
        if curl -s http://fan-club.kz/ | grep -q "chatContainer"; then
            echo "✅ AI виджет присутствует на странице"
        else
            echo "⚠️ AI виджет не найден на странице"
        fi
    else
        echo "❌ Главная страница не загружается"
    fi
else
    echo "❌ Сайт недоступен через nginx"
    echo "Проверьте конфигурацию nginx вручную"
fi

echo ""
echo "🏁 ВОССТАНОВЛЕНИЕ ЗАВЕРШЕНО!"
echo "============================="
echo ""
echo "📋 Что было сделано:"
echo "  • Проверен и запущен Django сервер"
echo "  • Создана временная nginx конфигурация без SSL"
echo "  • Перезагружен nginx"
echo "  • Проверена доступность сайта"
echo ""
echo "💡 Если сайт все еще недоступен:"
echo "  1. Проверьте права доступа к nginx конфигурации"
echo "  2. Убедитесь, что Django сервер работает на порту 8000"
echo "  3. Проверьте firewall настройки"
echo "  4. Проверьте DNS настройки домена"