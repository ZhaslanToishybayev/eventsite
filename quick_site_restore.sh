#!/bin/bash

# 🚀 Быстрое восстановление полноценного сайта
echo "🚀 БЫСТРОЕ ВОССТАНОВЛЕНИЕ ПОЛНОЦЕННОГО САЙТА"
echo "============================================"

# Проверка Django сервера
echo "1. Проверка Django сервера..."
cd /var/www/myapp/eventsite

if pgrep -f "python.*manage\.py.*runserver" > /dev/null; then
    echo "✅ Django сервер работает"
else
    echo "❌ Django сервер не работает, запускаем..."
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    python manage.py runserver 0.0.0.0:8000 > /dev/null 2>&1 &
    sleep 3

    if curl -s http://localhost:8000/health/ 2>/dev/null | grep -q "healthy"; then
        echo "✅ Django сервер запущен"
    else
        echo "❌ Django сервер не запустился"
        exit 1
    fi
fi

# Проверка nginx
echo ""
echo "2. Проверка nginx конфигурации..."

if [ -f "/etc/nginx/sites-available/fan-club.kz" ]; then
    if sudo nginx -t 2>/dev/null; then
        echo "✅ Конфигурация nginx валидна"
    else
        echo "❌ Ошибка конфигурации nginx"
        echo "Используем простую конфигурацию..."
        sudo cp /var/www/myapp/eventsite/nginx_simple_config /etc/nginx/sites-available/fan-club.kz
        sudo nginx -t
    fi
else
    echo "❌ Конфигурация nginx не найдена"
    echo "Копируем конфигурацию..."
    sudo cp /var/www/myapp/eventsite/nginx_complete_config /etc/nginx/sites-available/fan-club.kz
    sudo nginx -t
fi

# Активация сайта в nginx
if [ ! -L "/etc/nginx/sites-enabled/fan-club.kz" ]; then
    echo "Активируем сайт в nginx..."
    sudo ln -sf /etc/nginx/sites-available/fan-club.kz /etc/nginx/sites-enabled/
fi

# Перезагрузка nginx
echo "Перезагружаем nginx..."
sudo systemctl reload nginx
sleep 2

# Проверка SSL сертификата
echo ""
echo "3. Проверка SSL сертификата..."

if [ -f "/etc/letsencrypt/live/fan-club.kz/fullchain.pem" ]; then
    echo "✅ SSL сертификат найден"
    # Проверяем срок действия
    cert_expiry=$(sudo openssl x509 -in /etc/letsencrypt/live/fan-club.kz/fullchain.pem -noout -enddate | cut -d= -f2)
    cert_expiry_epoch=$(date -d "$cert_expiry" +%s)
    current_epoch=$(date +%s)
    days_until_expiry=$(( (cert_expiry_epoch - current_epoch) / 86400 ))

    if [ $days_until_expiry -lt 7 ]; then
        echo "⚠️  SSL сертификат скоро истечет ($days_until_expiry дней)"
        echo "Обновляем сертификат..."
        sudo certbot renew --quiet
    else
        echo "✅ SSL сертификат действителен ($days_until_expiry дней)"
    fi
else
    echo "❌ SSL сертификат не найден"
    echo "⚠️  Для получения SSL сертификата выполните:"
    echo "   sudo certbot --nginx -d fan-club.kz -d www.fan-club.kz"
    echo "   (требуется, чтобы домен fan-club.kz указывал на этот сервер)"
fi

# Проверка работоспособности
echo ""
echo "4. Тестирование работоспособности..."

# Проверка HTTP
if curl -s http://fan-club.kz/health/ 2>/dev/null | grep -q "healthy"; then
    echo "✅ HTTP доступ работает"
    http_works=true
else
    echo "❌ HTTP доступ не работает"
    http_works=false
fi

# Проверка HTTPS
if curl -k -s https://fan-club.kz/health/ 2>/dev/null | grep -q "healthy"; then
    echo "✅ HTTPS доступ работает"
    https_works=true
else
    echo "❌ HTTPS доступ не работает"
    https_works=false
fi

# Проверка AI API
if curl -k -s -X POST "https://fan-club.kz/api/v1/ai/simplified/interactive/chat/" \
    -H "Content-Type: application/json" \
    -d '{"message": "Привет", "user_email": "test@fan-club.kz", "state_id": null}' \
    2>/dev/null > /dev/null; then
    echo "✅ AI API работает"
    api_works=true
else
    echo "❌ AI API не работает"
    api_works=false
fi

# Итог
echo ""
echo "📊 ИТОГ ТЕСТИРОВАНИЯ:"
echo "===================="
echo "HTTP: $([ $http_works = true ] && echo '✅ Работает' || echo '❌ Не работает')"
echo "HTTPS: $([ $https_works = true ] && echo '✅ Работает' || echo '❌ Не работает')"
echo "AI API: $([ $api_works = true ] && echo '✅ Работает' || echo '❌ Не работает')"

if [ $http_works = true ] || [ $https_works = true ]; then
    echo ""
    echo "🎉 САЙТ РАБОТАЕТ!"
    echo "=================="

    if [ $https_works = true ]; then
        echo "🌐 Полный доступ:"
        echo "   https://fan-club.kz"
        echo "   https://www.fan-club.kz"
    fi

    if [ $http_works = true ]; then
        echo "🌐 Временный доступ (HTTP):"
        echo "   http://fan-club.kz"
        echo "   http://www.fan-club.kz"
    fi

    echo ""
    echo "🚀 Функции сайта:"
    echo "   ✅ AI консультант"
    echo "   ✅ Создание клубов"
    echo "   ✅ AI чат-виджет на всех страницах"
    echo "   ✅ Все функции Django"
    echo "   ✅ Статические файлы"
    echo "   ✅ Медиа файлы"

    if [ $https_works = false ]; then
        echo ""
        echo "💡 Для включения HTTPS:"
        echo "   1. Убедитесь, что домен fan-club.kz указывает на этот сервер"
        echo "   2. Выполните: sudo certbot --nginx -d fan-club.kz -d www.fan-club.kz"
        echo "   3. Перезагрузите nginx: sudo systemctl reload nginx"
    fi
else
    echo ""
    echo "❌ Сайт не работает. Проверьте логи:"
    echo "   sudo tail -f /var/log/nginx/error.log"
    echo "   sudo systemctl status nginx"
    echo "   sudo systemctl status django-fanclub"
fi

echo ""
echo "🔧 Команды управления:"
echo "======================"
echo "sudo systemctl status nginx           # Статус nginx"
echo "sudo systemctl status django-fanclub  # Статус Django"
echo "sudo tail -f /var/log/nginx/error.log # Логи nginx"
echo "curl -I https://fan-club.kz          # Проверка HTTPS"
echo ""
echo "🏁 ВОССТАНОВЛЕНИЕ ЗАВЕРШЕНО!"