#!/bin/bash
# 🚀 UnitySphere - Быстрая настройка nginx для работы сайта

echo "🚀 UnitySphere - Настройка nginx"
echo "=================================="

# Проверяем, запущены ли сервисы
echo "🔍 Проверяем запущенные сервисы..."

if curl -s http://127.0.0.1:8000/ > /dev/null; then
    echo "✅ Django сервер работает на порту 8000"
else
    echo "❌ Django сервер не работает на порту 8000"
    echo "Запускаем Django..."
    cd /var/www/myapp/eventsite
    source venv/bin/activate
    python manage.py runserver 127.0.0.1:8000 --insecure &
    sleep 5
fi

if curl -s http://127.0.0.1:8001/api/v1/ai/production/health/ > /dev/null; then
    echo "✅ AI агент работает на порту 8001"
else
    echo "❌ AI агент не работает на порту 8001"
    echo "Запускаем AI агент..."
    cd /var/www/myapp/eventsite
    python standalone_ai_server_updated.py &
    sleep 3
fi

# Копируем nginx конфигурацию
echo "🔧 Настраиваем nginx конфигурацию..."
sudo cp /var/www/myapp/eventsite/nginx_unitysphere_working.conf /etc/nginx/sites-available/unitysphere

# Активируем конфигурацию
echo "🔌 Активируем nginx конфигурацию..."
sudo ln -sf /etc/nginx/sites-available/unitysphere /etc/nginx/sites-enabled/unitysphere

# Отключаем default сайт
echo "🚫 Отключаем default сайт..."
sudo rm -f /etc/nginx/sites-enabled/default

# Проверяем конфигурацию nginx
echo "✅ Проверяем nginx конфигурацию..."
if sudo nginx -t; then
    echo "✅ Конфигурация nginx валидна"
else
    echo "❌ Ошибка в конфигурации nginx"
    exit 1
fi

# Перезагружаем nginx
echo "🔄 Перезагружаем nginx..."
sudo nginx -s reload 2>/dev/null || sudo systemctl reload nginx 2>/dev/null || true

# Проверяем, что nginx работает
sleep 2
if curl -s http://127.0.0.1/ > /dev/null; then
    echo "✅ nginx успешно перенаправляет на Django сайт"
    echo "🌐 Сайт доступен по адресу: http://127.0.0.1/"
else
    echo "❌ nginx не перенаправляет на Django сайт"
    echo "Проверим вручную..."
    sudo systemctl status nginx
fi

echo ""
echo "📋 Финальный статус:"
echo "Django: http://127.0.0.1:8000/"
echo "AI Agent: http://127.0.0.1:8001/"
echo "Nginx: http://127.0.0.1/"
echo ""
echo "🎉 UnitySphere сайт теперь работает через nginx!"
echo "🤖 AI виджет должен быть доступен на главной странице"