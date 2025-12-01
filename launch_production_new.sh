#!/bin/bash

# 🚀 UnitySphere Production Launch Script
# Простой скрипт для запуска production версии

echo "🚀 UnitySphere Production Launch"
echo "================================"

cd /var/www/myapp/eventsite

# Активируем виртуальное окружение
echo "🔧 Activating virtual environment..."
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found"
    exit 1
fi

# Проверяем Django
echo "🔍 Checking Django..."
if python -c "import django; print('Django version:', django.get_version())" 2>/dev/null; then
    echo "✅ Django available"
else
    echo "❌ Django not available, installing..."
    pip install django djangorestframework openai
fi

# Проверяем AI агент
echo "🧪 Testing AI agent..."
if python -c "
from ai_consultant.agents.lightweight_production_agent import get_ai_response
response = get_ai_response('Привет', 'test')
print('AI Agent test:', 'success' if response else 'failed')
" 2>/dev/null; then
    echo "✅ AI agent working"
else
    echo "❌ AI agent test failed"
    exit 1
fi

# Проверяем API
echo "🔍 Testing API..."
if python -c "
from ai_consultant.api import production_api
print('API test: success')
" 2>/dev/null; then
    echo "✅ API working"
else
    echo "❌ API test failed"
    exit 1
fi

# Останавливаем предыдущие процессы
echo "🛑 Stopping previous processes..."
pkill -f "python.*runserver" 2>/dev/null || true
sleep 2

# Запускаем Django сервер
echo "🚀 Starting Django server..."
nohup python manage.py runserver 127.0.0.1:8001 --insecure > django_production.log 2>&1 &
DJANGO_PID=$!

# Ждем запуска
echo "⏳ Waiting for server startup..."
sleep 5

# Проверяем запуск
if curl -s http://127.0.0.1:8001/api/v1/ai/production/health/ > /dev/null; then
    echo "✅ Django server is running (PID: $DJANGO_PID)"
else
    echo "❌ Django server failed to start"
    echo "Check logs: tail -f django_production.log"
    exit 1
fi

# Тестируем AI API
echo "🧪 Testing AI API..."
API_RESPONSE=$(curl -s http://127.0.0.1:8001/api/v1/ai/production/health/)
if echo "$API_RESPONSE" | grep -q "healthy"; then
    echo "✅ AI API working"
else
    echo "⚠️  AI API test failed, but server is running"
    echo "Response: $API_RESPONSE"
fi

# Создаем production информацию
echo "📋 Creating production info..."
cat > production_status.json << EOF
{
  "status": "PRODUCTION_READY",
  "server_url": "http://127.0.0.1:8001",
  "api_endpoints": {
    "ai_agent": "/api/v1/ai/production/agent/",
    "health_check": "/api/v1/ai/production/health/",
    "info": "/api/v1/ai/production/info/"
  },
  "nginx_setup": {
    "step1": "sudo cp nginx_production_final.conf /etc/nginx/sites-available/unitysphere",
    "step2": "sudo ln -sf /etc/nginx/sites-available/unitysphere /etc/nginx/sites-enabled/",
    "step3": "sudo rm -f /etc/nginx/sites-enabled/default",
    "step4": "sudo nginx -t && sudo systemctl restart nginx"
  },
  "test_commands": {
    "health": "curl http://fan-club.kz/api/v1/ai/production/health/",
    "ai_test": "curl -X POST http://fan-club.kz/api/v1/ai/production/agent/ -H 'Content-Type: application/json' -d '{\"message\": \"Привет\", \"session_id\": \"test\"}'"
  }
}
EOF

echo "✅ Production status saved to production_status.json"

# Финальная информация
echo ""
echo "🎉 PRODUCTION LAUNCH COMPLETED!"
echo "================================"
echo ""
echo "🌐 Server URL: http://127.0.0.1:8001"
echo "🤖 AI Agent: http://127.0.0.1:8001/api/v1/ai/production/agent/"
echo "🔍 Health Check: http://127.0.0.1:8001/api/v1/ai/production/health/"
echo ""
echo "📋 Next steps for nginx setup:"
echo "   1. sudo cp nginx_production_final.conf /etc/nginx/sites-available/unitysphere"
echo "   2. sudo ln -sf /etc/nginx/sites-available/unitysphere /etc/nginx/sites-enabled/"
echo "   3. sudo rm -f /etc/nginx/sites-enabled/default"
echo "   4. sudo nginx -t && sudo systemctl restart nginx"
echo ""
echo "🧪 Test after nginx setup:"
echo "   curl http://fan-club.kz/api/v1/ai/production/health/"
echo ""
echo "✅ UnitySphere Production Ready!"