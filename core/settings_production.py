"""
Production Django Settings for UnitySphere
"""

from .settings import *
import os

# SECURITY SETTINGS FOR PRODUCTION
DEBUG = False
ALLOWED_HOSTS = ['fan-club.kz', 'www.fan-club.kz', '77.243.80.110']

# PRODUCTION DATABASE (PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_NAME', 'unitysphere_prod'),
        'USER': os.getenv('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('POSTGRES_HOST', 'localhost'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
        'OPTIONS': {
            'connect_timeout': 60,
            'application_name': 'unitysphere_app',
        },
        'CONN_MAX_AGE': 60,  # Persistent connections
    }
}

# REDIS CACHE CONFIGURATION
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{os.getenv('REDIS_HOST', 'localhost')}:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 50,
                "retry_on_timeout": True,
                "health_check_interval": 30,
            }
        },
        "KEY_PREFIX": "unitysphere",
        "TIMEOUT": 300,  # 5 минут по умолчанию
    }
}

# SESSION BACKEND (Redis)
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# PRODUCTION SECURITY SETTINGS
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 год
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# CSRF AND COOKIES
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_TRUSTED_ORIGINS = ['https://fan-club.kz', 'https://www.fan-club.kz']
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True

# X-FRAME-OPTIONS
X_FRAME_OPTIONS = 'DENY'

# LOGGING CONFIGURATION
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'json': {
            'format': '{"level": "{levelname}", "time": "{asctime}", "module": "{module}", "message": "{message}"}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_false'],
            'class': 'logging.StreamHandler',
            'formatter': 'json'
        },
        'file': {
            'level': 'INFO',
            'filters': ['require_debug_false'],
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/unitysphere/django.log',
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 5,
            'formatter': 'json'
        },
        'error_file': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/unitysphere/django_errors.log',
            'maxBytes': 1024*1024*5,   # 5MB
            'backupCount': 5,
            'formatter': 'json'
        },
        'ai_monitoring': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/unitysphere/ai_monitoring.log',
            'maxBytes': 1024*1024*20,  # 20MB
            'backupCount': 10,
            'formatter': 'json'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'INFO',
            'propagate': True,
        },
        'ai_consultant': {
            'handlers': ['console', 'file', 'ai_monitoring'],
            'level': 'INFO',
            'propagate': True,
        },
        'core.monitoring': {
            'handlers': ['console', 'ai_monitoring'],
            'level': 'INFO',
            'propagate': False,
        },
        'core.security': {
            'handlers': ['console', 'error_file'],
            'level': 'WARNING',
            'propagate': True,
        },
        'clubs': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'accounts': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# PERFORMANCE SETTINGS
USE_TZ = True
TIME_ZONE = 'Asia/Almaty'

# STATIC FILES FOR PRODUCTION
STATIC_ROOT = '/var/www/unitysphere/static/'
MEDIA_ROOT = '/var/www/unitysphere/media/'

# EMAIL CONFIGURATION (Production)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@fan-club.kz')

# RATE LIMITING IN PRODUCTION
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'

# DJANGO-CONSTANCE FOR DYNAMIC SETTINGS
INSTALLED_APPS += [
    'constance',
    'constance.backends.database',
]

CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'
CONSTANCE_DATABASE_CACHE_BACKEND = 'default'

# DYNAMIC CONFIGURATION FIELDS
CONSTANCE_CONFIG = {
    'AI_RATE_LIMIT_PER_MINUTE': (30, 'AI requests per minute per IP', int),
    'MAX_FILE_SIZE_MB': (10, 'Maximum file size in MB', int),
    'MAINTENANCE_MODE': (False, 'Enable maintenance mode', bool),
    'NEW_REGISTRATIONS_ENABLED': (True, 'Enable new user registrations', bool),
}

# CONNECTION POOLING
CONN_MAX_AGE = 60
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB

# SECURITY MIDDLEWARE UPDATES
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Для статических файлов
    'corsheaders.middleware.CorsMiddleware',
    'core.security.SecurityHeadersMiddleware',
    'core.monitoring.AIMonitoringMiddleware',
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

# ADDITIONAL APPS FOR PRODUCTION
INSTALLED_APPS += [
    'django_extensions',  # Для утилит командной строки
]

# WHITENOISE FOR STATIC FILES
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# MONITORING AND HEALTH CHECKS
HEALTH_CHECK_ENABLED = True

# SENTRY FOR ERROR TRACKING (опционально)
SENTRY_DSN = os.getenv('SENTRY_DSN')
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration(
            transaction_style='url',
        )],
        traces_sample_rate=0.1,
        send_default_pii=False
    )