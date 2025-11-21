"""
Enhanced database configuration with connection pooling
"""

import os
import dj_database_url
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def get_database_config():
    """
    Возвращает конфигурацию базы данных с connection pooling
    """
    if settings.DEBUG:
        # Для разработки используем SQLite
        return {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': settings.BASE_DIR / 'db.sqlite3',
            'OPTIONS': {
                'timeout': 20,
            }
        }
    else:
        # Для production используем PostgreSQL с пулом соединений
        return {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('POSTGRES_NAME', 'unitysphere_prod'),
            'USER': os.getenv('POSTGRES_USER', 'postgres'),
            'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
            'HOST': os.getenv('POSTGRES_HOST', 'localhost'),
            'PORT': os.getenv('POSTGRES_PORT', '5432'),
            'OPTIONS': {
                'connect_timeout': 60,
                'application_name': 'unitysphere_app',
                # Connection pooling настройки
                'MAX_CONNS': 20,
                'MIN_CONNS': 5,
                'server_side_binding': True,
            },
            'CONN_MAX_AGE': 60,  # Persistent connections
            'ATOMIC_REQUESTS': True,  # Каждая request обернута в транзакцию
        }


class DatabaseRouter:
    """
    Router для разделения чтения/записи (для future scaling)
    """

    def db_for_read(self, model, **hints):
        """
        Подразумевает использование read replica
        """
        if hasattr(model, '_state') and model._state.db:
            return model._state.db
        return 'default'

    def db_for_write(self, model, **hints):
        """
        Всегда пишет в primary database
        """
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """
        Позволяет связи только внутри одной БД
        """
        db_set = {'default'}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Разрешает миграции только на primary DB
        """
        return db == 'default'


def optimize_postgres_settings():
    """
    Возвращает SQL команды для оптимизации PostgreSQL
    """
    return [
        # Оптимизация памяти
        "SET shared_buffers = '256MB';",
        "SET effective_cache_size = '1GB';",
        "SET maintenance_work_mem = '64MB';",
        "SET checkpoint_completion_target = 0.9;",

        # Оптимизация для работы с JSON
        "SET gin_fuzzy_search_limit = 500;",
        "SET gin_pending_list_limit = '4MB';",

        # Время ожидания
        "SET statement_timeout = '300s';",
        "SET lock_timeout = '30s';",
        "SET idle_in_transaction_session_timeout = '60s';",

        # Оптимизация запросов
        "SET random_page_cost = 1.1;",
        "SET effective_io_concurrency = 200;",
    ]


def get_health_check_sql():
    """
    SQL запросы для health check базы данных
    """
    return [
        "SELECT 1 as health_check;",  # Базовая проверка
        "SELECT count(*) as total_users FROM accounts_user;",  # Проверка данных
        "SELECT count(*) as active_clubs FROM clubs_club WHERE is_active = true;",
        "SELECT count(*) as total_chats FROM ai_consultant_chatsession WHERE created_at > NOW() - INTERVAL '24 hours';",
    ]


def monitor_connection_pool():
    """
    Возвращает информацию о connection pool
    """
    try:
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    count(*) as total_connections,
                    count(CASE WHEN state = 'active' THEN 1 END) as active_connections,
                    count(CASE WHEN state = 'idle' THEN 1 END) as idle_connections,
                    max(backend_start) as oldest_connection
                FROM pg_stat_activity
                WHERE datname = current_database();
            """)

            result = cursor.fetchone()

            return {
                'total_connections': result[0] if result else 0,
                'active_connections': result[1] if result else 0,
                'idle_connections': result[2] if result else 0,
                'oldest_connection': result[3] if result else None,
            }

    except Exception as e:
        logger.error(f"Error monitoring connection pool: {e}")
        return {}


class ConnectionPoolMiddleware:
    """
    Middleware для мониторинга connection pool
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Логируем информацию о соединениях при каждом запросе (в DEBUG режиме)
        if settings.DEBUG:
            pool_info = monitor_connection_pool()
            logger.info(f"Connection pool info: {pool_info}")

        response = self.get_response(request)

        return response