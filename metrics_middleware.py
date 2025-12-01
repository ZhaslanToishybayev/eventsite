"""
📊 Django Metrics Middleware для UnitySphere AI
Сбор метрик для Prometheus и аналитики
"""
import time
import threading
from django.utils.deprecation import MiddlewareMixin
from django.db import connection
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest
from django.http import HttpResponse

# 📊 Prometheus Metrics Registry
registry = CollectorRegistry()

# 🤖 AI-specific metrics
ai_requests_total = Counter(
    'ai_requests_total',
    'Total number of AI requests',
    ['method', 'endpoint', 'status'],
    registry=registry
)

ai_response_time_seconds = Histogram(
    'ai_response_time_seconds',
    'AI request response time in seconds',
    ['method', 'endpoint'],
    registry=registry
)

ai_errors_total = Counter(
    'ai_errors_total',
    'Total number of AI errors',
    ['error_type', 'endpoint'],
    registry=registry
)

ai_active_sessions = Gauge(
    'ai_active_sessions',
    'Number of active AI sessions',
    registry=registry
)

ai_tokens_used_total = Counter(
    'ai_tokens_used_total',
    'Total number of tokens used in AI requests',
    ['model'],
    registry=registry
)

# 🌐 Django application metrics
django_requests_total = Counter(
    'django_requests_total',
    'Total number of Django requests',
    ['method', 'endpoint', 'status'],
    registry=registry
)

django_db_queries_total = Counter(
    'django_db_queries_total',
    'Total number of database queries',
    ['model'],
    registry=registry
)

django_db_query_duration_seconds = Histogram(
    'django_db_query_duration_seconds',
    'Database query duration',
    ['query_type'],
    registry=registry
)

# 🏢 Club-specific metrics
club_requests_total = Counter(
    'club_requests_total',
    'Total number of club-related requests',
    ['action', 'status'],
    registry=registry
)

club_creations_total = Counter(
    'club_creations_total',
    'Total number of club creations',
    ['category'],
    registry=registry
)

development_requests_total = Counter(
    'development_requests_total',
    'Total number of development requests',
    ['action'],
    registry=registry
)

# 📊 Session metrics
user_sessions_active = Gauge(
    'user_sessions_active',
    'Number of active user sessions',
    registry=registry
)

# 🧵 Thread-local storage for request metrics
_local = threading.local()


class MetricsMiddleware(MiddlewareMixin):
    """Middleware for collecting application metrics"""

    def process_request(self, request):
        """Начало обработки запроса"""
        _local.start_time = time.time()
        _local.db_queries_before = len(connection.queries)
        _local.request_method = request.method
        _local.request_path = self._get_endpoint_name(request.path)

    def process_response(self, request, response):
        """Конец обработки запроса"""
        if hasattr(_local, 'start_time'):
            # 📊 Calculate response time
            response_time = time.time() - _local.start_time

            # 🏷️ Determine endpoint type
            endpoint = getattr(_local, 'request_path', 'unknown')
            method = getattr(_local, 'request_method', request.method)

            # 🤖 AI-specific metrics
            if '/api/v1/ai/' in request.path:
                self._track_ai_metrics(request, response, response_time, method, endpoint)

            # 🌐 Django metrics
            django_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status=response.status_code
            ).inc()

            # 💾 Database metrics
            self._track_db_metrics(method, endpoint)

            # 🏢 Business metrics
            self._track_business_metrics(request, response)

        return response

    def process_exception(self, request, exception):
        """Обработка исключений"""
        if hasattr(_local, 'request_path'):
            endpoint = _local.request_path
            method = getattr(_local, 'request_method', request.method)

            # 🚨 Error metrics
            ai_errors_total.labels(
                error_type=type(exception).__name__,
                endpoint=endpoint
            ).inc()

            django_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status=500
            ).inc()

    def _get_endpoint_name(self, path):
        """Определение имени endpoint для метрик"""
        # 🤖 AI endpoints
        if '/api/v1/ai/simple-chat/' in path:
            return 'ai_simple_chat'
        elif '/api/v1/ai/chat/' in path:
            return 'ai_chat'
        elif '/api/v1/ai/club-creation/' in path:
            return 'ai_club_creation'
        elif '/api/v1/ai/development/' in path:
            return 'ai_development'
        elif '/api/v1/ai/feedback/' in path:
            return 'ai_feedback'
        elif '/api/v1/ai/interview/' in path:
            return 'ai_interview'

        # 🌐 Django endpoints
        elif '/clubs/' in path:
            return 'clubs'
        elif '/accounts/' in path:
            return 'accounts'
        elif '/admin/' in path:
            return 'admin'
        elif path == '/':
            return 'home'
        else:
            return 'other'

    def _track_ai_metrics(self, request, response, response_time, method, endpoint):
        """Отслеживание AI-специфичных метрик"""
        ai_response_time_seconds.labels(
            method=method,
            endpoint=endpoint
        ).observe(response_time)

        ai_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status=response.status_code
        ).inc()

        # 🤖 Track tokens if available in response
        if hasattr(response, 'data') and isinstance(response.data, dict):
            tokens_used = response.data.get('tokens_used')
            if tokens_used:
                ai_tokens_used_total.labels(
                    model=response.data.get('model', 'unknown')
                ).inc(tokens_used)

    def _track_db_metrics(self, method, endpoint):
        """Отслеживание метрик базы данных"""
        if hasattr(_local, 'db_queries_before'):
            queries_after = len(connection.queries)
            new_queries = queries_after - _local.db_queries_before

            if new_queries > 0:
                django_db_queries_total.labels(
                    model='general'  # Could be enhanced to track specific models
                ).inc(new_queries)

    def _track_business_metrics(self, request, response):
        """Отслеживание бизнес-метрик"""
        path = request.path

        # 🏢 Club metrics
        if '/api/v1/ai/club-creation/' in path and response.status_code == 201:
            action = self._extract_club_action(path)
            club_requests_total.labels(
                action=action,
                status='success' if response.status_code < 400 else 'error'
            ).inc()

        # 🎯 Development metrics
        if '/api/v1/ai/development/' in path:
            action = self._extract_development_action(path)
            development_requests_total.labels(action=action).inc()

    def _extract_club_action(self, path):
        """Определение действия с клубами"""
        if 'ideas' in path:
            return 'ideas'
        elif 'names' in path:
            return 'names'
        elif 'description' in path:
            return 'description'
        elif 'monetization' in path:
            return 'monetization'
        elif 'plan' in path:
            return 'plan'
        else:
            return 'other'

    def _extract_development_action(self, path):
        """Определение действия с развитием"""
        if 'paths' in path:
            return 'paths'
        elif 'progress' in path:
            return 'progress'
        elif 'plan' in path:
            return 'plan'
        else:
            return 'other'


# 📊 Metrics endpoint
def metrics_view(request):
    """Endpoint for Prometheus metrics"""
    return HttpResponse(
        generate_latest(registry),
        content_type='text/plain; charset=utf-8'
    )


# 🔄 Session counter (simple implementation)
def update_session_metrics():
    """Обновление метрик сессий"""
    from django.contrib.sessions.models import Session
    from django.utils import timezone

    active_sessions = Session.objects.filter(
        expire_date__gt=timezone.now()
    ).count()

    user_sessions_active.set(active_sessions)

    # 🤖 AI sessions
    try:
        from ai_consultant.models import ChatSession
        active_ai_sessions = ChatSession.objects.filter(is_active=True).count()
        ai_active_sessions.set(active_ai_sessions)
    except:
        pass  # Model might not exist


# 🚀 Auto-update session metrics
import atexit
import threading
import time

def _session_metrics_updater():
    """Background thread for updating session metrics"""
    while True:
        try:
            update_session_metrics()
        except Exception:
            pass  # Silent fail
        time.sleep(60)  # Update every minute

# Start background thread
session_thread = threading.Thread(target=_session_metrics_updater, daemon=True)
session_thread.start()

atexit.register(lambda: session_thread.join(timeout=5))