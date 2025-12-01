"""
🚨 Sentry Error Tracking для UnitySphere AI
Production-ready error monitoring and performance tracking
"""
import os

# 🔥 Sentry Configuration
def setup_sentry():
    """Настройка Sentry для error tracking и performance monitoring"""
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.redis import RedisIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    from sentry_sdk.integrations.argv import ArgvIntegration

    # 🎯 Sentry DSN из environment variables
    SENTRY_DSN = os.getenv('SENTRY_DSN')
    if not SENTRY_DSN:
        print("⚠️ Sentry DSN not configured - error tracking disabled")
        return

    # 🔧 Sentry Configuration
    sentry_logging = LoggingIntegration(
        level=os.getenv('SENTRY_LOG_LEVEL', 'INFO').upper(),        # Capture info and above as breadcrumbs
        event_level=os.getenv('SENTRY_EVENT_LEVEL', 'ERROR').upper()  # Send errors as events
    )

    sentry_sdk.init(
        dsn=SENTRY_DSN,

        # 🎯 Environment
        environment=os.getenv('SENTRY_ENVIRONMENT', 'development'),

        # 🏷️ Release tracking
        release=os.getenv('SENTRY_RELEASE', 'unitysphere-ai@1.0.0'),

        # 🔗 Integrations
        integrations=[
            DjangoIntegration(
                transaction_style='url',
                middleware_spans=True,
                signals_spans=True,
            ),
            RedisIntegration(),
            CeleryIntegration(),
            sentry_logging,
            ArgvIntegration(),
        ],

        # 📊 Performance Monitoring
        traces_sample_rate=float(os.getenv('SENTRY_TRACES_SAMPLE_RATE', '0.1')),  # 10% of transactions

        # 🎯 Error filtering
        before_send=before_send_filter,

        # 🛡️ Data scrubbing
        send_default_pii=False,  # Don't send personal data by default

        # 📝 Additional configuration
        attach_stacktrace=True,
        with_locals=True,
        auto_enabling_assert_hook=False,
        auto_enabling_exceptions_hook=False,
        auto_enabling_threads_hook=False,
    )

    print("🚨 Sentry Error Tracking initialized")


def before_send_filter(event, hint):
    """Фильтрация событий перед отправкой в Sentry"""
    # 🚫 Filter out specific errors
    if 'exc_info' in hint:
        exc_type, exc_value, tb = hint['exc_info']

        # Skip specific exceptions
        if exc_type.__name__ in [
            'DoesNotExist',
            'ValidationError',
            'PermissionDenied',
            'NotFound'
        ]:
            return None

        # Skip 404 errors from bots/scanners
        if hasattr(exc_value, 'status_code') and exc_value.status_code == 404:
            request = event.get('request', {})
            user_agent = request.get('headers', {}).get('User-Agent', '')
            if any(bot in user_agent.lower() for bot in [
                'bot', 'crawler', 'scanner', 'curl', 'wget'
            ]):
                return None

    return event


# 📊 Custom metrics for UnitySphere AI
class SentryMetrics:
    """Кастомные метрики для UnitySphere AI"""

    @staticmethod
    def track_ai_request(message_type, response_time, success=True):
        """Отслеживание AI запросов"""
        import sentry_sdk

        with sentry_sdk.configure_scope() as scope:
            scope.set_tag("ai_message_type", message_type)
            scope.set_tag("ai_success", success)
            scope.set_extra("response_time_ms", response_time)

            if success:
                sentry_sdk.capture_message(
                    f"AI request completed: {message_type}",
                    level="info"
                )
            else:
                sentry_sdk.capture_message(
                    f"AI request failed: {message_type}",
                    level="error"
                )

    @staticmethod
    def track_club_creation(user_id, club_name, success=True):
        """Отслеживание создания клубов"""
        import sentry_sdk

        with sentry_sdk.configure_scope() as scope:
            scope.set_tag("feature", "club_creation")
            scope.set_tag("success", success)
            scope.user = {"id": user_id}
            scope.set_extra("club_name", club_name)

            sentry_sdk.capture_message(
                f"Club creation attempt: {club_name}",
                level="info" if success else "error"
            )

    @staticmethod
    def track_development_plan(user_id, path_title, success=True):
        """Отслеживание планов развития"""
        import sentry_sdk

        with sentry_sdk.configure_scope() as scope:
            scope.set_tag("feature", "development_plan")
            scope.set_tag("success", success)
            scope.user = {"id": user_id}
            scope.set_extra("path_title", path_title)

            sentry_sdk.capture_message(
                f"Development plan creation: {path_title}",
                level="info" if success else "error"
            )


# 🎯 Performance monitoring decorators
def monitor_ai_performance(func_name=None):
    """Декоратор для мониторинга производительности AI функций"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            import time
            import sentry_sdk

            start_time = time.time()
            function_name = func_name or f"{func.__module__}.{func.__name__}"

            with sentry_sdk.start_transaction(op="ai_function", name=function_name):
                try:
                    result = func(*args, **kwargs)
                    execution_time = (time.time() - start_time) * 1000  # ms

                    # Track success
                    sentry_sdk.set_tag("ai_function", function_name)
                    sentry_sdk.set_tag("status", "success")
                    sentry_sdk.set_measurement("execution_time_ms", execution_time)

                    return result

                except Exception as e:
                    execution_time = (time.time() - start_time) * 1000  # ms

                    # Track error
                    sentry_sdk.set_tag("ai_function", function_name)
                    sentry_sdk.set_tag("status", "error")
                    sentry_sdk.set_measurement("execution_time_ms", execution_time)
                    sentry_sdk.capture_exception(e)

                    raise

        return wrapper
    return decorator


# 📈 Health check integration
def health_check_report():
    """Генерация health check отчета для Sentry"""
    import sentry_sdk
    from django.db import connection
    from django.core.cache import cache

    health_status = {
        'database': 'healthy',
        'cache': 'healthy',
        'ai_service': 'healthy',
        'timestamp': '2025-11-26T16:45:00Z'
    }

    # Check database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception:
        health_status['database'] = 'unhealthy'

    # Check cache
    try:
        cache.set('health_check', 'ok', 10)
        if cache.get('health_check') != 'ok':
            health_status['cache'] = 'unhealthy'
    except Exception:
        health_status['cache'] = 'unhealthy'

    # Check AI service
    try:
        from ai_consultant.services_v2 import AIConsultantServiceV2
        service = AIConsultantServiceV2()
        # Simple check if service can be initialized
    except Exception:
        health_status['ai_service'] = 'unhealthy'

    # Send to Sentry
    with sentry_sdk.configure_scope() as scope:
        scope.set_tag("health_check", "system")
        for component, status in health_status.items():
            scope.set_tag(f"component_{component}", status)

        sentry_sdk.capture_message(
            f"Health check: {health_status}",
            level="info"
        )

    return health_status


# 🚨 Error handlers for Django
def sentry_500_handler(request):
    """Custom 500 error handler with Sentry"""
    import sentry_sdk
    from sentry_sdk import capture_exception
    import sys

    # Capture the exception
    capture_exception(sys.exc_info()[1])

    # Add request context
    with sentry_sdk.configure_scope() as scope:
        scope.set_tag("error_handler", "500")
        scope.set_extra("request_path", request.path)
        scope.set_extra("request_method", request.method)

    # Return generic error response
    from django.http import JsonResponse
    return JsonResponse({
        'error': 'Internal server error',
        'message': 'An error occurred. Our team has been notified.',
        'request_id': sentry_sdk.last_event_id()
    }, status=500)


def sentry_404_handler(request, exception):
    """Custom 404 error handler with Sentry"""
    import sentry_sdk

    # Only capture 404s that might be important
    with sentry_sdk.configure_scope() as scope:
        scope.set_tag("error_handler", "404")
        scope.set_extra("request_path", request.path)
        scope.set_extra("exception", str(exception))

        # Don't send to Sentry for obvious bot requests
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        if not any(bot in user_agent.lower() for bot in ['bot', 'crawler', 'scanner']):
            sentry_sdk.capture_message(f"404: {request.path}", level="warning")

    from django.http import JsonResponse
    return JsonResponse({
        'error': 'Not found',
        'message': 'The requested resource was not found.'
    }, status=404)