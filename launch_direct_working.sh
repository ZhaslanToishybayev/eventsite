#!/bin/bash
# 🚀 UnitySphere - Прямой запуск Django с AI интеграцией (без nginx)

echo "🚀 UnitySphere - Прямой запуск Django с AI интеграцией"
echo "========================================================="

# Останавливаем предыдущие процессы
echo "🛑 Останавливаем предыдущие процессы..."
pkill -f "python.*manage.py.*runserver" 2>/dev/null || true
pkill -f "python.*standalone_ai" 2>/dev/null || true

# Активируем виртуальное окружение
echo "🔧 Активируем виртуальное окружение..."
cd /var/www/myapp/eventsite
source venv/bin/activate

# Проверяем Django конфигурацию
echo "✅ Проверяем Django конфигурацию..."
python manage.py check --deploy

# Запускаем Django на порту 8000
echo "🌐 Запускаем Django на порту 8000..."
python manage.py runserver 127.0.0.1:8000 --insecure &
DJANGO_PID=$!

# Ждем запуска Django
sleep 5

# Проверяем Django
if curl -s http://127.0.0.1:8000/ > /dev/null; then
    echo "✅ Django успешно запущен на порту 8000"
else
    echo "❌ Django не запущен"
    exit 1
fi

# Запускаем AI агент на порту 8001
echo "🤖 Запускаем AI агент на порту 8001..."
python standalone_ai_server_updated.py &
AI_PID=$!

# Ждем запуска AI агента
sleep 3

# Проверяем AI агента
if curl -s http://127.0.0.1:8001/api/v1/ai/production/health/ > /dev/null; then
    echo "✅ AI агент успешно запущен на порту 8001"
else
    echo "❌ AI агент не запущен"
    exit 1
fi

# Проверяем AI прокси в Django
echo "🔗 Проверяем AI прокси в Django..."
if curl -s http://127.0.0.1:8000/api/v1/ai/production/health/ > /dev/null; then
    echo "✅ AI прокси работает"
else
    echo "❌ AI прокси не работает"
fi

echo ""
echo "📋 Финальный статус:"
echo "Django: http://127.0.0.1:8000/"
echo "AI Agent: http://127.0.0.1:8001/"
echo "AI Proxy: http://127.0.0.1:8000/api/v1/ai/production/agent/"
echo ""
echo "🎉 UnitySphere сайт работает!"
echo "🤖 AI виджет доступен на Django сайте"
echo ""
echo "Django PID: $DJANGO_PID"
echo "AI Agent PID: $AI_PID"
echo ""
echo "🌐 Теперь можно заходить на сайт и пользоваться AI консультантом!"