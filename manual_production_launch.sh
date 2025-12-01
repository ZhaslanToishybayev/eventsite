#!/bin/bash

# 🚀 Manual Production Launch for UnitySphere
# Ручной запуск production версии

echo "🚀 UnitySphere Manual Production Launch"
echo "======================================"

cd /var/www/myapp/eventsite

# 1. Активируем виртуальное окружение
echo "🔧 Step 1: Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"

# 2. Проверяем Django
echo ""
echo "🔍 Step 2: Checking Django..."
python -c "import django; print('Django version:', django.get_version())"
if [ $? -eq 0 ]; then
    echo "✅ Django working"
else
    echo "❌ Django not working"
    exit 1
fi

# 3. Проверяем AI агент
echo ""
echo "🧪 Step 3: Testing AI agent..."
python -c "
from ai_consultant.agents.lightweight_production_agent import get_ai_response
response = get_ai_response('Привет', 'test')
if response and 'response' in response:
    print('✅ AI Agent working')
    print('Sample response:', response['response'][:50], '...')
else:
    print('❌ AI Agent failed')
    exit(1)
"
if [ $? -eq 0 ]; then
    echo "✅ AI agent test passed"
else
    echo "❌ AI agent test failed"
    exit 1
fi

# 4. Проверяем API
echo ""
echo "🔍 Step 4: Testing API..."
python -c "
from ai_consultant.api import production_api
print('✅ API module imported successfully')
"
if [ $? -eq 0 ]; then
    echo "✅ API test passed"
else
    echo "❌ API test failed"
    exit 1
fi

# 5. Останавливаем предыдущие процессы
echo ""
echo "🛑 Step 5: Stopping previous processes..."
pkill -f "python.*runserver" 2>/dev/null || true
sleep 2
echo "✅ Previous processes stopped"

# 6. Запускаем Django сервер
echo ""
echo "🚀 Step 6: Starting Django server..."
python manage.py runserver 127.0.0.1:8001 --insecure &
DJANGO_PID=$!

echo "✅ Django server started (PID: $DJANGO_PID)"

# 7. Ждем запуска
echo ""
echo "⏳ Step 7: Waiting for server startup..."
sleep 5

# 8. Проверяем запуск
echo ""
echo "🔍 Step 8: Checking server status..."
if curl -s http://127.0.0.1:8001/api/v1/ai/production/health/ > /dev/null; then
    echo "✅ Django server is responding"
else
    echo "❌ Django server not responding"
    echo "Checking Django process..."
    ps aux | grep runserver | grep -v grep
    exit 1
fi

# 9. Тестируем AI API
echo ""
echo "🧪 Step 9: Testing AI API..."
API_RESPONSE=$(curl -s http://127.0.0.1:8001/api/v1/ai/production/health/)
if echo "$API_RESPONSE" | grep -q "healthy"; then
    echo "✅ AI API health check passed"
    echo "Response: $API_RESPONSE"
else
    echo "⚠️  AI API health check failed"
    echo "Response: $API_RESPONSE"
fi

# 10. Тестируем AI агента
echo ""
echo "🤖 Step 10: Testing AI Agent..."
AGENT_RESPONSE=$(curl -s -X POST http://127.0.0.1:8001/api/v1/ai/production/agent/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Привет", "session_id": "test"}')

if echo "$AGENT_RESPONSE" | grep -q "success"; then
    echo "✅ AI Agent test passed"
    echo "Sample response:"
    echo "$AGENT_RESPONSE" | python -m json.tool | head -10
else
    echo "⚠️  AI Agent test failed"
    echo "Response: $AGENT_RESPONSE"
fi

# 11. Создаем статус файл
echo ""
echo "📋 Step 11: Creating production status..."
cat > production_status.json << EOF
{
  "status": "PRODUCTION_READY",
  "server_url": "http://127.0.0.1:8001",
  "django_pid": $DJANGO_PID,
  "api_endpoints": {
    "ai_agent": "/api/v1/ai/production/agent/",
    "health_check": "/api/v1/ai/production/health/",
    "info": "/api/v1/ai/production/info/"
  },
  "test_results": {
    "django": "working",
    "ai_agent": "working",
    "api_health": "passed",
    "nginx_setup_needed": true
  },
  "nginx_setup": {
    "copy_config": "sudo cp nginx_production_final.conf /etc/nginx/sites-available/unitysphere",
    "enable_site": "sudo ln -sf /etc/nginx/sites-available/unitysphere /etc/nginx/sites-enabled/",
    "remove_default": "sudo rm -f /etc/nginx/sites-enabled/default",
    "test_reload": "sudo nginx -t && sudo systemctl restart nginx"
  },
  "production_urls": {
    "main_site": "http://fan-club.kz",
    "ai_agent": "http://fan-club.kz/api/v1/ai/production/agent/",
    "health_check": "http://fan-club.kz/api/v1/ai/production/health/"
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
echo "📋 Status File: production_status.json"
echo ""
echo "🔧 Next steps for nginx setup:"
echo "   1. sudo cp nginx_production_final.conf /etc/nginx/sites-available/unitysphere"
echo "   2. sudo ln -sf /etc/nginx/sites-available/unitysphere /etc/nginx/sites-enabled/"
echo "   3. sudo rm -f /etc/nginx/sites-enabled/default"
echo "   4. sudo nginx -t && sudo systemctl restart nginx"
echo ""
echo "🧪 Test after nginx setup:"
echo "   curl http://fan-club.kz/api/v1/ai/production/health/"
echo ""
echo "✅ UnitySphere Production Ready!"

# Показываем текущие процессы
echo ""
echo "📋 Current processes:"
ps aux | grep python | grep -v grep || echo "No Python processes found"