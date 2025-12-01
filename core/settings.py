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

# 🔐 Безопасные настройки для Development
DEBUG = True

ALLOWED_HOSTS = ['77.243.80.110', 'localhost', '127.0.0.1', 'fan-club.kz', 'www.fan-club.kz', '0.0.0.0']
CSRF_TRUSTED_ORIGINS = ['https://fan-club.kz', 'https://www.fan-club.kz', 'https://fan-club.kz', 'https://77.243.80.110']

# 🔒 Security Headers (Development)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'SAMEORIGIN'

# 🛡️ HTTPS Settings
SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# 🛡️ Content Security Policy (Production) - Optimized for performance
CONTENT_SECURITY_POLICY = {
    'DIRECTIVES': {
        'base-uri': ("'self'",),
        'connect-src': ("'self'", "https://api.openai.com", "https://fonts.googleapis.com"),
        'default-src': ("'self'",),
        'font-src': ("'self'", "https://fonts.gstatic.com"),
        'form-action': ("'self'",),
        'frame-src': ("'self'",),
        'img-src': ("'self'", "data:", "https://*.gravatar.com"),
        'object-src': ("'none'",),
        'script-src': ("'self'", "'unsafe-inline'", "https://kit.fontawesome.com"),
        'style-src': ("'self'", "'unsafe-inline'", "https://fonts.googleapis.com"),
        'style-src-elem': ("'self'", "'unsafe-inline'", "https://fonts.googleapis.com"),
    }
}

# 🚀 Кэширование (Production Optimized for 2GB RAM)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'OPTIONS': {
            'MAX_ENTRIES': 500,  # Reduced for 2GB RAM
            'CULL_FREQUENCY': 2,  # Cull 1/2 of entries when max is reached
        }
    }
}

# 📊 Session settings (Optimized for 2GB RAM)
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_COOKIE_AGE = 3600  # Reduced to 1 hour for better memory usage
SESSION_SAVE_EVERY_REQUEST = False  # Only save when session data changes

# ⚡ Performance settings (Optimized for 2GB RAM)
CONN_MAX_AGE = 60  # Enable persistent connections for better performance
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
    'csp',  # Content Security Policy
    'django_filters',
    'ckeditor',
    'sslserver',  # SSL server for development

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
    'core.middleware.HTTPToHTTPSRedirectMiddleware',  # Перенаправление HTTP на HTTPS
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'csp.middleware.CSPMiddleware',  # Content Security Policy
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

SITE_ID = 2

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
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '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')

# AI System Configuration from ai_settings.py
# GPT-4o mini API Configuration
OPENAI_API_BASE = "https://api.openai.com/v1"
OPENAI_MODEL = "gpt-4o-mini"
OPENAI_TEMPERATURE = 0.7
OPENAI_MAX_TOKENS = 1500
OPENAI_TIMEOUT = 30

# AI System Configuration
AI_ENABLED = True
AI_CONSULTANT_ENABLED = True
AI_RECOMMENDATIONS_ENABLED = True
AI_CLUB_CREATION_ENABLED = True

# Rate Limiting
AI_RATE_LIMIT_REQUESTS = 60  # requests per minute
AI_RATE_LIMIT_WINDOW = 60    # seconds

# Caching Configuration
AI_CACHE_TIMEOUT = 300  # 5 minutes
AI_CACHE_ENABLED = True

# Context Configuration
AI_CONTEXT_WINDOW = 10  # Number of previous messages to consider
AI_RECOMMENDATION_LIMIT = 5  # Max recommendations per response
AI_SEARCH_LIMIT = 20  # Max search results

# RAG (Retrieval-Augmented Generation) Configuration
AI_RAG_ENABLED = True
AI_RAG_SIMILARITY_THRESHOLD = 0.7
AI_RAG_MAX_DOCUMENTS = 5

# Logging Configuration
AI_LOG_LEVEL = "INFO"
AI_LOG_REQUESTS = True
AI_LOG_RESPONSES = False  # Set to True for debugging

# Error Handling
AI_RETRY_ATTEMPTS = 3
AI_RETRY_DELAY = 1  # seconds
AI_FALLBACK_ENABLED = True

# Performance Configuration
AI_ASYNC_ENABLED = True
AI_BATCH_PROCESSING_ENABLED = False
AI_PARALLEL_REQUESTS = 5

# Performance Optimizations for 2GB RAM Server
# Disable migrations in production for better performance
MIGRATION_MODULES = {}

# Reduce logging level for production
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',  # Reduced from INFO to WARNING
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'ai_consultant': {
            'handlers': ['console'],
            'level': 'WARNING',  # Reduced logging for AI components
            'propagate': False,
        },
    },
}
