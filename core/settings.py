import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

import os
from datetime import timedelta
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', '%7T15&=Z4E@wKBjTy}6{3QTfxeW_h~je4,fi867-COb+s1oD6o')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['77.243.80.110', 'localhost', '127.0.0.1', 'fan-club.kz', 'www.fan-club.kz']
CSRF_TRUSTED_ORIGINS = ['https://fan-club.kz', 'https://www.fan-club.kz', 'https://fan-club.kz',]
USE_X_FORWARDED_HOST = True
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'django_filters',
    'ckeditor',

    'accounts',
    'clubs',
    'ai_consultant',
    'agents',

    # Allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'core.security.SecurityHeadersMiddleware',  # Новые security заголовки
    'core.monitoring.AIMonitoringMiddleware',   # Мониторинг AI запросов
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'accounts.middleware.RequirePhoneMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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


DATABASES = {
    # Для разработки используем SQLite
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
    # Для продакшена PostgreSQL
    # 'default': {
    #     'ENGINE': 'django.db.backends.postgresql',
    #     'NAME': os.getenv('POSTGRES_NAME'),
    #     'USER': os.getenv('POSTGRES_USER'),
    #     'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
    #     'HOST': os.getenv('POSTGRES_HOST'),
    #     'PORT': os.getenv('POSTGRES_PORT'),
    #     'DISABLE_SERVER_SIDE_CURSORS': True,
    # }
}

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1

# Provider specific settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}

# Redirect to home URL after login (Default: /accounts/profile/)
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_ON_GET = True

# Allauth settings for custom user model
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_UNIQUE_EMAIL = True

ACCOUNT_ADAPTER = 'accounts.adapters.CustomAccountAdapter'
SOCIALACCOUNT_ADAPTER = 'accounts.adapters.CustomSocialAccountAdapter'

# Social Account Settings
SOCIALACCOUNT_AUTO_SIGNUP = True
ACCOUNT_EMAIL_VERIFICATION = 'none'  # Don't require email verification for now


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


AUTH_USER_MODEL = 'accounts.User'

# LOGIN_REDIRECT_URL = 'index'
# LOGOUT_REDIRECT_URL = 'index'

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Asia/Almaty'

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


#CACHES = {
#    "default": {
#        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
#    }
#}
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    }
}

CORS_ALLOWED_ORIGINS = [
    'http://localhost:8000',
]


REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    )
}

# CKEditor Settings
CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_IMAGE_BACKEND = "pillow"
CKEDITOR_JQUERY_URL = '//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js'
CKEDITOR_CONFIGS = {
    'default':
        {
            'toolbar': 'full',
            'width': 'auto',
            'extraPlugins': ','.join([
                'codesnippet',
            ]),
        },
}

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Serena AI Configuration
SERENA_ENABLED = os.getenv('SERENA_ENABLED', 'True').lower() == 'true'
SERENA_URL = os.getenv('SERENA_URL', 'http://localhost:8001')
SERENA_TIMEOUT = int(os.getenv('SERENA_TIMEOUT', '30'))
SERENA_PROJECT_PATH = os.getenv('SERENA_PROJECT_PATH', '/home/zhaslan/Downloads/unitysphere-project/home/almalinux/new/unitysphere')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')  # Upgraded for Function Calling support
OPENAI_MAX_TOKENS = int(os.getenv('OPENAI_MAX_TOKENS', '1000'))
OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', '0.7'))

# AI Consultant Settings
AI_CONSULTANT_ENABLED = os.getenv('AI_CONSULTANT_ENABLED', 'True').lower() == 'true'
AI_CONSULTANT_MAX_HISTORY_MESSAGES = int(os.getenv('AI_CONSULTANT_MAX_HISTORY_MESSAGES', '10'))
AI_CONSULTANT_MAX_SESSIONS_PER_USER = int(os.getenv('AI_CONSULTANT_MAX_SESSIONS_PER_USER', '50'))

# Google OAuth Configuration
SOCIALACCOUNTS_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'APP': {
            'client_id': os.getenv('GOOGLE_CLIENT_ID'),
            'secret': os.getenv('GOOGLE_CLIENT_SECRET'),
            'key': os.getenv('GOOGLE_CLIENT_ID'),
        }
    }
}
