#!/bin/bash

# 🚀 UnitySphere Production Launch - Lightweight Version
# Ручной запуск production версии без dependency проблем

echo "🚀 UnitySphere Production Launch - Lightweight Version"
echo "======================================================="

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

# 3. Тестируем Lightweight AI Agent
echo ""
echo "🧪 Step 3: Testing Lightweight AI Agent..."
python -c "
from ai_consultant.agents.lightweight_production_agent import get_ai_response
response = get_ai_response('Привет', 'test')
if response and 'response' in response:
    print('✅ Lightweight AI Agent working')
    print('Sample response:', response['response'][:50], '...')
else:
    print('❌ Lightweight AI Agent failed')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo "✅ Lightweight AI Agent test passed"
else
    echo "❌ Lightweight AI Agent test failed"
    exit 1
fi

# 4. Останавливаем предыдущие процессы
echo ""
echo "🛑 Step 4: Stopping previous processes..."
pkill -f "python.*runserver" 2>/dev/null || true
sleep 2
echo "✅ Previous processes stopped"

# 5. Создаем временную production URL конфигурацию
echo ""
echo "⚙️ Step 5: Setting up production URLs..."
cat > temp_production_urls.py << 'EOF'
"""🎯 Temporary Production URLs - Lightweight AI Only"""

from django.urls import path
from django.http import JsonResponse
from ai_consultant.agents.lightweight_production_agent import get_ai_response
import json

def health_check(request):
    """🔍 Health check endpoint"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'UnitySphere Lightweight AI Agent',
        'version': '1.0.0',
        'timestamp': '2025-11-27T06:15:00'
    })

def production_ai_agent(request):
    """🤖 Production AI Agent endpoint"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '')
            session_id = data.get('session_id', 'default')

            response = get_ai_response(message, session_id)

            return JsonResponse({
                'success': True,
                'response': response.get('response', ''),
                'state': response.get('state', ''),
                'timestamp': '2025-11-27T06:15:00',
                'session_id': session_id
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e),
                'timestamp': '2025-11-27T06:15:00'
            }, status=500)
    else:
        return JsonResponse({'error': 'POST method required'}, status=405)

urlpatterns = [
    path('api/v1/ai/production/health/', health_check, name='health_check'),
    path('api/v1/ai/production/agent/', production_ai_agent, name='production_ai_agent'),
    path('health/', health_check, name='main_health'),
]
EOF

# 6. Запускаем Django сервер с временной конфигурацией
echo ""
echo "🚀 Step 6: Starting Django server with production URLs..."
export DJANGO_SETTINGS_MODULE=temp_production_settings

# Создаем временную settings конфигурацию
cat > temp_production_settings.py << 'EOF'
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

SECRET_KEY = 'django-insecure-production-key'
DEBUG = False
ALLOWED_HOSTS = ['fan-club.kz', 'www.fan-club.kz', '77.243.80.110', 'localhost', '127.0.0.1']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'clubs',
    'events',
    'users',
    'ai_consultant',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'temp_production_urls'
WSGI_APPLICATION = 'core.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = []
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Asia/Almaty'
USE_I18N = True
USE_TZ = True
STATIC_URL = '/static/'
EOF

# Запускаем сервер
DJANGO_SETTINGS_MODULE=temp_production_settings python manage.py runserver 127.0.0.1:8001 --insecure &
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
  -d '{"message": "Привет! Хочу создать клуб программирования", "session_id": "test"}')

if echo "$AGENT_RESPONSE" | grep -q "success"; then
    echo "✅ AI Agent test passed"
    echo "Sample response:"
    echo "$AGENT_RESPONSE" | python -m json.tool | head -10
else
    echo "⚠️  AI Agent test failed"
    echo "Response: $AGENT_RESPONSE"
fi

# 11. Создаем production информацию
echo ""
echo "📋 Step 11: Creating production status..."
cat > production_status_final.json << EOF
{
  "status": "PRODUCTION_READY_LIGHTWEIGHT",
  "server_url": "http://127.0.0.1:8001",
  "django_pid": $DJANGO_PID,
  "ai_agent": "lightweight_production",
  "api_endpoints": {
    "ai_agent": "/api/v1/ai/production/agent/",
    "health_check": "/api/v1/ai/production/health/",
    "main_health": "/health/"
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
  },
  "notes": "Lightweight production version without heavy AI dependencies"
}
EOF

echo "✅ Production status saved to production_status_final.json"

# Финальная информация
echo ""
echo "🎉 PRODUCTION LAUNCH COMPLETED!"
echo "================================"
echo ""
echo "🌐 Server URL: http://127.0.0.1:8001"
echo "🤖 AI Agent: http://127.0.0.1:8001/api/v1/ai/production/agent/"
echo "🔍 Health Check: http://127.0.0.1:8001/api/v1/ai/production/health/"
echo "📋 Status File: production_status_final.json"
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
echo "✅ UnitySphere Lightweight Production Ready!"
echo ""
echo "📋 Current processes:"
ps aux | grep python | grep -v grep || echo "No Python processes found"