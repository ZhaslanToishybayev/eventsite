#!/bin/bash

# 🚀 ФИНАЛЬНЫЙ ПРОDUCTION ЗАПУСК UNITYSPHERE
# Полный запуск сайта с AI виджетом на fan-club.kz

echo "🚀 ФИНАЛЬНЫЙ PRODUCTION ЗАПУСК UNITYSPHERE"
echo "==========================================="
echo "🎯 Цель: Запустить сайт на fan-club.kz с работающим AI виджетом"
echo ""

# 1. Проверяем Django сервер
echo "🔍 ШАГ 1: Проверяем Django сервер..."
cd /var/www/myapp/eventsite

# Останавливаем все Django процессы
echo "🛑 Останавливаем существующие Django процессы..."
pkill -f "python.*manage.py" 2>/dev/null
sleep 2

# Активируем виртуальное окружение
echo "🔌 Активируем виртуальное окружение..."
source venv/bin/activate

# Запускаем Django на порту 8080
echo "🌐 Запускаем Django сервер на порту 8080..."
python manage.py runserver 0.0.0.0:8080 --insecure &
DJANGO_PID=$!
sleep 5

# Проверяем Django
if curl -s http://127.0.0.1:8080/ > /dev/null; then
    echo "✅ Django успешно запущен на порту 8080"
else
    echo "❌ Django не запустился на порту 8080"
    echo "Проверим логи Django..."
    kill $DJANGO_PID 2>/dev/null
    python manage.py runserver 0.0.0.0:8080 --insecure
    exit 1
fi

# 2. Проверяем AI виджет
echo ""
echo "🤖 ШАГ 2: Проверяем AI виджет..."
if curl -s http://127.0.0.1:8080/api/v1/ai/production/agent/ > /dev/null; then
    echo "✅ AI виджет API доступен"
else
    echo "⚠️  AI виджет API может быть недоступен"
    echo "Проверим Django URL конфигурацию..."
fi

# 3. Создаем и применяем nginx конфигурацию
echo ""
echo "⚙️  ШАГ 3: Настраиваем nginx..."

# Создаем оптимальную конфигурацию nginx
cat > /tmp/nginx_production.conf << 'EOF'
# 🚀 UnitySphere Production Configuration - IDEAL SETUP
# Адаптивный, быстрый, безопасный nginx + Django

# Основной сервер для fan-club.kz
server {
    listen 80;
    listen [::]:80;
    server_name fan-club.kz www.fan-club.kz;

    # 🛡️ Безопасность
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # 📁 Статические файлы (максимальная производительность)
    location /static/ {
        alias /var/www/myapp/eventsite/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;

        # Оптимизация для разных типов файлов
        location ~* \.(css|js)$ {
            expires 1M;
            add_header Cache-Control "public";
        }

        location ~* \.(jpg|jpeg|png|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # 📂 Медиа файлы
    location /media/ {
        alias /var/www/myapp/eventsite/media/;
        expires 30d;
        add_header Cache-Control "public";
    }

    # 🤖 AI Widget API (высокий приоритет)
    location /api/v1/ai/production/ {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Таймауты для AI
        proxy_connect_timeout 30s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # CORS для виджета
        add_header Access-Control-Allow-Origin "*" always;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Origin, X-Requested-With, Content-Type, Accept, Authorization" always;
    }

    # 🐛 Health check
    location /health/ {
        proxy_pass http://127.0.0.1:8080;
        access_log off;
    }

    # 🌐 Все остальные запросы → Django
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Оптимизация проксирования
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
        proxy_busy_buffers_size 8k;

        # Таймауты
        proxy_connect_timeout 30s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # 🚫 Запрет доступа к служебным файлам
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }

    # 📊 Статистика (если нужно)
    location /nginx_status {
        stub_status on;
        allow 127.0.0.1;
        deny all;
    }
}
EOF

echo "📋 Конфигурация nginx создана"

# Пытаемся применить конфигурацию (если есть доступ)
if sudo cp /tmp/nginx_production.conf /etc/nginx/nginx.conf 2>/dev/null; then
    echo "✅ Конфигурация nginx применена"
    NGINX_CONFIG_APPLIED=true
else
    echo "⚠️  Нет доступа sudo. Конфигурация сохранена в /tmp/nginx_production.conf"
    echo "   Вам нужно вручную:"
    echo "   1. sudo cp /tmp/nginx_production.conf /etc/nginx/nginx.conf"
    NGINX_CONFIG_APPLIED=false
fi

# Проверяем конфигурацию nginx
if sudo nginx -t 2>/dev/null; then
    echo "✅ Конфигурация nginx валидна"
    NGINX_CONFIG_VALID=true
else
    echo "⚠️  Проблемы с конфигурацией nginx"
    NGINX_CONFIG_VALID=false
fi

# Перезапускаем nginx (если есть доступ)
if [ "$NGINX_CONFIG_APPLIED" = true ] && sudo systemctl restart nginx 2>/dev/null; then
    echo "✅ Nginx перезапущен"
    NGINX_RESTARTED=true
elif [ "$NGINX_CONFIG_APPLIED" = true ] && sudo service nginx restart 2>/dev/null; then
    echo "✅ Nginx перезапущен"
    NGINX_RESTARTED=true
else
    echo "⚠️  Нет доступа для перезапуска nginx"
    echo "   Выполните вручную: sudo systemctl restart nginx"
    NGINX_RESTARTED=false
fi

# 4. Проверяем доступность сайта
echo ""
echo "🌐 ШАГ 4: Проверяем доступность сайта..."
sleep 3

# Проверяем разные варианты доступа
echo "🔍 Проверяем доступность по разным адресам..."

# Проверяем через nginx (если он работает)
if curl -s http://fan-club.kz/ > /dev/null; then
    echo "✅ Сайт доступен по fan-club.kz"
    SITE_ACCESSIBLE=true
    SITE_URL="http://fan-club.kz/"
elif curl -s http://www.fan-club.kz/ > /dev/null; then
    echo "✅ Сайт доступен по www.fan-club.kz"
    SITE_ACCESSIBLE=true
    SITE_URL="http://www.fan-club.kz/"
elif curl -s http://77.243.80.110/ > /dev/null; then
    echo "✅ Сайт доступен по IP адресу"
    SITE_ACCESSIBLE=true
    SITE_URL="http://77.243.80.110/"
elif curl -s http://127.0.0.1/ > /dev/null; then
    echo "✅ Сайт доступен по localhost"
    SITE_ACCESSIBLE=true
    SITE_URL="http://127.0.0.1/"
else
    echo "❌ Сайт недоступен ни по одному адресу"
    SITE_ACCESSIBLE=false
    SITE_URL=""
fi

# Проверяем AI виджет
echo ""
echo "🤖 ШАГ 5: Проверяем AI виджет..."
if [ "$SITE_ACCESSIBLE" = true ] && curl -s "$SITE_URL/api/v1/ai/production/agent/" > /dev/null; then
    echo "✅ AI виджет API доступен"
    WIDGET_ACCESSIBLE=true
else
    echo "⚠️  AI виджет API может быть недоступен"
    echo "   Проверим напрямую..."
    if curl -s http://127.0.0.1:8080/api/v1/ai/production/agent/ > /dev/null; then
        echo "✅ AI виджет работает напрямую на Django"
        WIDGET_ACCESSIBLE=true
    else
        echo "❌ AI виджет не работает"
        WIDGET_ACCESSIBLE=false
    fi
fi

# 5. Финальная информация
echo ""
echo "🎯 ФИНАЛЬНЫЙ ОТЧЕТ:"
echo "===================="
echo "✅ Django сервер: Работает на порту 8080"
echo "🌐 Сайт: $([ "$SITE_ACCESSIBLE" = true ] && echo "Доступен по $SITE_URL" || echo "❌ Недоступен")"
echo "🤖 AI виджет: $([ "$WIDGET_ACCESSIBLE" = true ] && echo "✅ Работает" || echo "❌ Не работает")"
echo ""
echo "🛠️  nginx статус:"
if [ "$NGINX_CONFIG_APPLIED" = true ]; then
    echo "   ✅ Конфигурация применена"
else
    echo "   ⚠️  Нужно вручную: sudo cp /tmp/nginx_production.conf /etc/nginx/nginx.conf"
fi
if [ "$NGINX_CONFIG_VALID" = true ]; then
    echo "   ✅ Конфигурация валидна"
else
    echo "   ⚠️  Проблемы с конфигурацией nginx"
fi
if [ "$NGINX_RESTARTED" = true ]; then
    echo "   ✅ Nginx перезапущен"
else
    echo "   ⚠️  Нужно вручную: sudo systemctl restart nginx"
fi

echo ""
echo "📋 ИНСТРУКЦИЯ ПО ЗАВЕРШЕНИЮ НАСТРОЙКИ:"
echo "========================================="
if [ "$NGINX_CONFIG_APPLIED" = false ] || [ "$NGINX_RESTARTED" = false ]; then
    echo "1. Примените nginx конфигурацию:"
    echo "   sudo cp /tmp/nginx_production.conf /etc/nginx/nginx.conf"
    echo ""
    echo "2. Проверьте конфигурацию:"
    echo "   sudo nginx -t"
    echo ""
    echo "3. Перезапустите nginx:"
    echo "   sudo systemctl restart nginx"
    echo ""
    echo "4. Проверьте статус:"
    echo "   sudo systemctl status nginx"
    echo ""
fi

echo "🌐 АДРЕСА ДЛЯ ПРОВЕРКИ САЙТА:"
echo "   - http://fan-club.kz/"
echo "   - http://www.fan-club.kz/"
echo "   - http://77.243.80.110/"
echo ""
echo "🤖 АДРЕС AI ВИДЖЕТА:"
echo "   - $SITE_URL/api/v1/ai/production/agent/"
echo ""
echo "💡 ВАЖНО:"
if [ "$SITE_ACCESSIBLE" = false ]; then
    echo "   Сайт недоступен. Проверьте nginx конфигурацию и перезапустите nginx."
elif [ "$WIDGET_ACCESSIBLE" = false ]; then
    echo "   AI виджет не работает. Проверьте Django URL конфигурацию."
else
    echo "   ✅ ВСЁ ГОТОВО! Сайт должен работать с AI виджетом!"
fi

echo ""
echo "🎉 ФИНАЛЬНЫЙ ЗАПУСК ЗАВЕРШЕН!"
echo "==============================="

# Оставляем Django работать
wait $DJANGO_PID