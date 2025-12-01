# 🚀 UnitySphere Production - Django Only (Working Solution)

# Останавливаем все процессы
pkill -f "python.*runserver" 2>/dev/null || true
pkill -f "python.*standalone_ai_server" 2>/dev/null || true

# Активируем виртуальное окружение
source venv/bin/activate

# Создаем временную URLs конфигурацию без AI проблем
cat > temp_urls_main.py << 'EOF'
"""🎯 Temporary Main URLs without AI dependencies"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Основные приложения
    path('', include('clubs.urls')),
    path('events/', include('events.urls')),
    path('users/', include('users.urls')),

    # AI Agent (lightweight, standalone)
    path('api/v1/ai/production/', include('ai_consultant.api.production_urls')),
]

# Статические файлы
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
EOF

# Заменяем проблемные URLs
cp core/urls.py core/urls_backup.py
cat > core/urls.py << 'EOF'
"""📋 Main URLs - Temporary working version"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Основные приложения
    path('', include('clubs.urls')),
    path('events/', include('events.urls')),
    path('users/', include('users.urls')),

    # AI Agent (lightweight, standalone)
    path('api/v1/ai/production/', include('ai_consultant.api.production_urls')),
]

# Статические файлы
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
EOF

echo "✅ Temporary URLs created without AI dependencies"

# Запускаем Django на порту 8000
python manage.py runserver 127.0.0.1:8000 --insecure &
DJANGO_PID=$

echo "✅ Django started with PID: $DJANGO_PID on port 8000"

# Ждем запуска
sleep 5

# Проверяем Django
if curl -s http://127.0.0.1:8000/ > /dev/null; then
    echo "✅ Django working on port 8000"
    echo "🔍 Testing main page..."
    curl -s http://127.0.0.1:8000/ | head -10
else
    echo "❌ Django not working on port 8000"
    echo "Checking Django process..."
    ps aux | grep runserver | grep -v grep
fi

# Запускаем AI агент на порту 8001
echo ""
echo "🚀 Starting AI Agent..."
python standalone_ai_server_updated.py &
AI_PID=$

sleep 3

# Проверяем AI агент
if curl -s http://127.0.0.1:8001/api/v1/ai/production/health/ > /dev/null; then
    echo "✅ AI Agent working on port 8001"
    echo "🔍 Testing AI health..."
    curl -s http://127.0.0.1:8001/api/v1/ai/production/health/ | python -m json.tool
else
    echo "❌ AI Agent not working on port 8001"
fi

echo ""
echo "📋 Final Status:"
echo "Django PID: $DJANGO_PID on port 8000"
echo "AI Agent PID: $AI_PID on port 8001"
echo ""
echo "🌐 Test URLs:"
echo "Django: http://127.0.0.1:8000/"
echo "AI Agent: http://127.0.0.1:8001/api/v1/ai/production/"