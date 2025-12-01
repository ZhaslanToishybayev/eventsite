#!/usr/bin/env python3
"""
🎯 Максимально простой запуск Django

Только ядро Django без сложных зависимостей.
"""

import os
import sys
from pathlib import Path

# Добавляем путь к проекту
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

def create_minimal_settings():
    """🔧 Создаем минимальные настройки Django"""

    settings_content = '''
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-minimal-key-for-testing-only'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '0.0.0.0', 'fan-club.kz', 'www.fan-club.kz']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'clubs',
    'accounts',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'minimal_urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Database - используем реальную базу данных
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = []

# Internationalization
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Asia/Almaty'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
'''

    with open('minimal_settings.py', 'w', encoding='utf-8') as f:
        f.write(settings_content)


def create_minimal_urls():
    """🔧 Создаем минимальные URL-ы"""

    urls_content = '''
from django.contrib import admin
from django.urls import path
from django.http import JsonResponse, HttpResponse
import json

def api_root(request):
    return JsonResponse({
        'name': 'UnitySphere Lightweight API',
        'version': 'v1',
        'status': 'active',
        'message': 'System is running with lightweight configuration',
        'endpoints': {
            'health': '/health/',
            'test': '/test/'
        }
    })

def health_check(request):
    return JsonResponse({
        'status': 'healthy',
        'service': 'Lightweight Django',
        'timestamp': '2024-11-26T23:30:00Z'
    })

def test_endpoint(request):
    # Тестируем облегченный агент
    try:
        from ai_consultant.agents.lightweight_agent import get_lightweight_agent

        agent = get_lightweight_agent()
        result = agent.process_message("Test message", "test_user")

        return JsonResponse({
            'status': 'success',
            'agent_test': 'passed',
            'response': result['response'][:50] + '...',
            'progress': f"{result['progress']['progress_percentage']}%",
            'intent': result['analysis']['intent']
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'agent_test': 'failed',
            'error': str(e)
        }, status=500)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/ai/health/', health_check, name='health'),
    path('api/v1/ai/test/', test_endpoint, name='test'),
    path('', api_root),
]
'''

    with open('minimal_urls.py', 'w', encoding='utf-8') as f:
        f.write(urls_content)


def main():
    """🎯 Главная функция"""

    print("🚀 Создание минимальной Django конфигурации...")
    print("=" * 50)

    try:
        # Создаем минимальные настройки
        create_minimal_settings()
        create_minimal_urls()
        print("✅ Минимальные настройки созданы")

        # Устанавливаем переменные окружения
        os.environ['DJANGO_SETTINGS_MODULE'] = 'minimal_settings'

        # Импортируем Django
        import django
        from django.conf import settings

        # Инициализируем Django
        django.setup()
        print("✅ Django инициализирован")

        # Импортируем manage.py
        from django.core.management import execute_from_command_line

        print("\n🚀 Запускаем Django development сервер...")
        print("📡 Сервер будет доступен на: http://127.0.0.1:8000")
        print("\n🔗 Доступные endpoints:")
        print("• GET / - API root")
        print("• GET /api/v1/ai/health/ - Health check")
        print("• GET /api/v1/ai/test/ - Test AI agent")

        # Запускаем сервер
        execute_from_command_line(['manage.py', 'runserver', '127.0.0.1:8000', '--insecure'])

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Запуск остановлен пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Ошибка: {e}")
        sys.exit(1)