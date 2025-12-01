#!/usr/bin/env python3
"""
🚀 Простой запуск Django с облегченными URL

Этот скрипт запускает Django с минимальными зависимостями.
"""

import os
import sys
import django
from pathlib import Path

# Добавляем путь к проекту
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Устанавливаем Django настройки
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

def setup_lightweight_urls():
    """🔧 Настройка облегченных URL"""

    # Создаем временный файл с облегченными URL
    lightweight_urls_content = '''
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def api_root(request):
    return JsonResponse({
        'name': 'UnitySphere Lightweight API',
        'version': 'v1',
        'status': 'active',
        'features': ['Club Creation Agent', 'Validation', 'Progress Tracking'],
        'endpoints': {
            'ai_agent': '/api/v1/ai/club-creation/agent/',
            'guide': '/api/v1/ai/club-creation/guide/',
            'categories': '/api/v1/ai/club-creation/categories/',
            'validate': '/api/v1/ai/club-creation/validate/',
            'health': '/api/v1/ai/health/'
        }
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('ai_consultant.api.lightweight_urls')),
    path('api/v1/ai/health/', lambda r: JsonResponse({'status': 'healthy'})),
    path('', api_root),
]
'''

    # Записываем временный файл
    with open('lightweight_urls_temp.py', 'w', encoding='utf-8') as f:
        f.write(lightweight_urls_content)

    return 'lightweight_urls_temp'


def main():
    """🎯 Главная функция запуска"""

    print("🚀 Запуск Django с облегченными URL...")
    print("=" * 50)

    try:
        # Инициализируем Django
        django.setup()
        print("✅ Django инициализирован")

        # Настраиваем облегченные URL
        urls_module = setup_lightweight_urls()
        print("✅ Облегченные URL настроены")

        # Импортируем и запускаем manage.py
        from django.core.management import execute_from_command_line

        # Заменяем ROOT_URLCONF временно
        os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings_lightweight'

        # Создаем легкие settings
        settings_content = '''
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-lightweight-key-for-testing'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '0.0.0.0']

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
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'lightweight_urls_temp'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.csrf',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
'''

        with open('settings_lightweight.py', 'w', encoding='utf-8') as f:
            f.write(settings_content)

        print("✅ Легкие настройки созданы")

        # Запускаем сервер
        print("\n🚀 Запускаем Django development сервер...")
        print("📡 Сервер будет доступен на: http://127.0.0.1:8000")

        execute_from_command_line(['manage.py', 'runserver', '127.0.0.1:8000', '--insecure'])

    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
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