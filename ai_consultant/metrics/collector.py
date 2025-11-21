import logging
from django.conf import settings

logger = logging.getLogger(__name__)

try:
    from prometheus_client import Counter, Histogram, Gauge
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logger.warning("prometheus_client not installed. Metrics will not be collected.")

class MetricsCollector:
    """
    Сборщик метрик для Prometheus
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MetricsCollector, cls).__new__(cls)
            cls._instance._initialize_metrics()
        return cls._instance
    
    def _initialize_metrics(self):
        if not PROMETHEUS_AVAILABLE:
            return
            
        # Метрики запросов
        self.ai_requests_total = Counter(
            'ai_consultant_requests_total',
            'Total AI consultant requests',
            ['status', 'type']
        )

        # Метрики времени ответа
        self.ai_response_time = Histogram(
            'ai_consultant_response_time_seconds',
            'AI consultant response time',
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
        )

        # Метрики токенов
        self.ai_tokens_used = Counter(
            'ai_consultant_tokens_used_total',
            'Total tokens used',
            ['model']
        )

        # Метрики ошибок
        self.ai_errors_total = Counter(
            'ai_consultant_errors_total',
            'Total AI consultant errors',
            ['type']
        )
        
        # Метрики кэша
        self.cache_hits = Counter(
            'ai_consultant_cache_hits_total',
            'Total cache hits'
        )
        
        self.cache_misses = Counter(
            'ai_consultant_cache_misses_total',
            'Total cache misses'
        )

    def record_request(self, status: str = 'success', request_type: str = 'chat'):
        """Запись метрики запроса"""
        if PROMETHEUS_AVAILABLE:
            self.ai_requests_total.labels(status=status, type=request_type).inc()

    def record_response_time(self, duration: float):
        """Запись времени ответа"""
        if PROMETHEUS_AVAILABLE:
            self.ai_response_time.observe(duration)

    def record_tokens(self, count: int, model: str = 'gpt-4o'):
        """Запись использованных токенов"""
        if PROMETHEUS_AVAILABLE:
            self.ai_tokens_used.labels(model=model).inc(count)

    def record_error(self, error_type: str):
        """Запись ошибки"""
        if PROMETHEUS_AVAILABLE:
            self.ai_errors_total.labels(type=error_type).inc()
            
    def record_cache_hit(self):
        """Запись попадания в кэш"""
        if PROMETHEUS_AVAILABLE:
            self.cache_hits.inc()
            
    def record_cache_miss(self):
        """Запись промаха кэша"""
        if PROMETHEUS_AVAILABLE:
            self.cache_misses.inc()
