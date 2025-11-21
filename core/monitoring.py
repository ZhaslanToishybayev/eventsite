import time
import logging
import json
from datetime import datetime, timedelta
from django.core.cache import cache
from django.db import models
from django.utils import timezone
from django.conf import settings
import threading

logger = logging.getLogger(__name__)


class AIMonitoringService:
    """
    Сервис мониторинга AI запросов и API потребления
    """

    CACHE_KEYS = {
        'daily_requests': 'ai_requests_daily',
        'hourly_requests': 'ai_requests_hourly',
        'api_usage': 'ai_api_usage',
        'error_rate': 'ai_error_rate',
        'response_times': 'ai_response_times'
    }

    def __init__(self):
        self.lock = threading.Lock()

    def track_request(self, request_data, response_data, processing_time, error=None):
        """
        Отслеживает AI запрос и записывает метрики
        """
        try:
            timestamp = timezone.now()

            # Базовые метрики
            metrics = {
                'timestamp': timestamp.isoformat(),
                'user_id': getattr(request_data.get('user'), 'id', None) if request_data.get('user') else None,
                'session_id': request_data.get('session_id'),
                'message_length': len(request_data.get('message', '')),
                'processing_time': processing_time,
                'tokens_used': response_data.get('tokens_used', 0),
                'response_length': len(response_data.get('response', '')),
                'success': error is None,
                'error_type': type(error).__name__ if error else None,
                'error_message': str(error) if error else None,
                'client_ip': request_data.get('client_ip'),
                'fallback_mode': response_data.get('fallback_mode', False)
            }

            # Обновляем счетчики в кэше
            self._update_cache_counters(metrics)

            # Записываем в лог
            self._log_request(metrics)

            # Проверяем на подозрительную активность
            self._check_suspicious_activity(metrics)

            # Обновляем статистику API потребления
            self._update_api_usage(metrics)

        except Exception as e:
            logger.error(f"Error tracking AI request: {e}")

    def _update_cache_counters(self, metrics):
        """
        Обновляет счетчики в кэше
        """
        try:
            with self.lock:
                # Ежедневные запросы
                daily_key = f"{self.CACHE_KEYS['daily_requests']}_{metrics['timestamp'][:10]}"
                daily_count = cache.get(daily_key, 0)
                cache.set(daily_key, daily_count + 1, timeout=86400)

                # Почасовые запросы
                hourly_key = f"{self.CACHE_KEYS['hourly_requests']}_{metrics['timestamp'][:13]}"
                hourly_count = cache.get(hourly_key, 0)
                cache.set(hourly_key, hourly_count + 1, timeout=3600)

                # Ошибки
                if not metrics['success']:
                    error_key = f"{self.CACHE_KEYS['error_rate']}_{metrics['timestamp'][:10]}"
                    error_count = cache.get(error_key, 0)
                    cache.set(error_key, error_count + 1, timeout=86400)

                # Время ответа
                times_key = f"{self.CACHE_KEYS['response_times']}_{metrics['timestamp'][:10]}"
                times = cache.get(times_key, [])
                times.append(metrics['processing_time'])
                if len(times) > 1000:  # Ограничиваем количество записей
                    times = times[-1000:]
                cache.set(times_key, times, timeout=86400)

        except Exception as e:
            logger.error(f"Error updating cache counters: {e}")

    def _log_request(self, metrics):
        """
        Записывает детальную информацию о запросе в лог
        """
        try:
            log_level = logging.WARNING if not metrics['success'] else logging.INFO

            log_data = {
                'user_id': metrics['user_id'],
                'session_id': metrics['session_id'],
                'processing_time': f"{metrics['processing_time']:.2f}s",
                'tokens_used': metrics['tokens_used'],
                'success': metrics['success'],
                'client_ip': metrics['client_ip'],
                'fallback_mode': metrics['fallback_mode']
            }

            if metrics['error_type']:
                log_data['error'] = f"{metrics['error_type']}: {metrics['error_message']}"

            logger.log(log_level, f"AI Request: {json.dumps(log_data)}")

        except Exception as e:
            logger.error(f"Error logging request: {e}")

    def _check_suspicious_activity(self, metrics):
        """
        Проверяет на подозрительную активность
        """
        try:
            suspicious_patterns = []

            # Много запросов от одного IP
            client_ip = metrics['client_ip']
            if client_ip:
                ip_requests_key = f"ai_requests_ip_{client_ip}_{metrics['timestamp'][:10]}"
                ip_requests = cache.get(ip_requests_key, 0) + 1
                cache.set(ip_requests_key, ip_requests, timeout=86400)

                if ip_requests > 100:  # Более 100 запросов в день от одного IP
                    suspicious_patterns.append(f"High request rate: {ip_requests}/day from IP {client_ip}")

            # Много запросов от одного пользователя
            if metrics['user_id']:
                user_requests_key = f"ai_requests_user_{metrics['user_id']}_{metrics['timestamp'][:10]}"
                user_requests = cache.get(user_requests_key, 0) + 1
                cache.set(user_requests_key, user_requests, timeout=86400)

                if user_requests > 200:  # Более 200 запросов в день от одного пользователя
                    suspicious_patterns.append(f"High request rate: {user_requests}/day from user {metrics['user_id']}")

            # Долгое время ответа
            if metrics['processing_time'] > 30:  # Более 30 секунд
                suspicious_patterns.append(f"Slow response: {metrics['processing_time']:.2f}s")

            # Много ошибок
            error_rate = self._calculate_error_rate()
            if error_rate > 0.5:  # Более 50% ошибок
                suspicious_patterns.append(f"High error rate: {error_rate:.1%}")

            # Если найдены подозрительные паттерны, логируем их
            if suspicious_patterns:
                alert_data = {
                    'timestamp': metrics['timestamp'],
                    'patterns': suspicious_patterns,
                    'metrics': {
                        'user_id': metrics['user_id'],
                        'client_ip': metrics['client_ip'],
                        'processing_time': metrics['processing_time']
                    }
                }
                logger.warning(f"Suspicious activity detected: {json.dumps(alert_data)}")

        except Exception as e:
            logger.error(f"Error checking suspicious activity: {e}")

    def _update_api_usage(self, metrics):
        """
        Обновляет статистику использования API
        """
        try:
            usage_key = f"{self.CACHE_KEYS['api_usage']}_{metrics['timestamp'][:10]}"

            current_usage = cache.get(usage_key, {
                'total_tokens': 0,
                'total_requests': 0,
                'total_cost': 0.0,
                'model_costs': {}
            })

            # Примерные цены (можно обновить согласно актуальным ценам OpenAI)
            model_costs = {
                'gpt-3.5-turbo': {'input': 0.0005, 'output': 0.0015},  # за 1K токенов
                'gpt-4': {'input': 0.03, 'output': 0.06},
                'gpt-4o-mini': {'input': 0.00015, 'output': 0.0006}
            }

            model = getattr(settings, 'OPENAI_MODEL', 'gpt-3.5-turbo')
            tokens = metrics['tokens_used']

            # Расчет стоимости (упрощенный)
            if model in model_costs and tokens > 0:
                cost = (tokens / 1000) * model_costs[model]['input']  # Предполагаем, что это input токены
            else:
                cost = 0.0

            current_usage['total_tokens'] += tokens
            current_usage['total_requests'] += 1
            current_usage['total_cost'] += cost

            if model not in current_usage['model_costs']:
                current_usage['model_costs'][model] = 0
            current_usage['model_costs'][model] += cost

            cache.set(usage_key, current_usage, timeout=86400)

        except Exception as e:
            logger.error(f"Error updating API usage: {e}")

    def _calculate_error_rate(self):
        """
        Рассчитывает процент ошибок за последние 24 часа
        """
        try:
            today = timezone.now().date().isoformat()

            requests_key = f"{self.CACHE_KEYS['daily_requests']}_{today}"
            errors_key = f"{self.CACHE_KEYS['error_rate']}_{today}"

            total_requests = cache.get(requests_key, 0)
            total_errors = cache.get(errors_key, 0)

            if total_requests == 0:
                return 0.0

            return total_errors / total_requests

        except Exception as e:
            logger.error(f"Error calculating error rate: {e}")
            return 0.0

    def get_daily_stats(self):
        """
        Возвращает статистику за сегодня
        """
        try:
            today = timezone.now().date().isoformat()

            requests_key = f"{self.CACHE_KEYS['daily_requests']}_{today}"
            errors_key = f"{self.CACHE_KEYS['error_rate']}_{today}"
            usage_key = f"{self.CACHE_KEYS['api_usage']}_{today}"
            times_key = f"{self.CACHE_KEYS['response_times']}_{today}"

            return {
                'date': today,
                'total_requests': cache.get(requests_key, 0),
                'total_errors': cache.get(errors_key, 0),
                'error_rate': self._calculate_error_rate(),
                'api_usage': cache.get(usage_key, {}),
                'avg_response_time': self._calculate_avg_response_time(cache.get(times_key, [])),
                'top_users': self._get_top_users(today),
                'top_ips': self._get_top_ips(today)
            }

        except Exception as e:
            logger.error(f"Error getting daily stats: {e}")
            return {}

    def _calculate_avg_response_time(self, times):
        """
        Рассчитывает среднее время ответа
        """
        try:
            if not times:
                return 0.0
            return sum(times) / len(times)
        except Exception:
            return 0.0

    def _get_top_users(self, date):
        """
        Возвращает топ пользователей по количеству запросов
        """
        try:
            top_users = []
            for key in cache.keys(f"ai_requests_user_*_{date}"):
                user_id = key.split('_')[3]
                count = cache.get(key, 0)
                top_users.append({'user_id': user_id, 'requests': count})

            return sorted(top_users, key=lambda x: x['requests'], reverse=True)[:10]
        except Exception:
            return []

    def _get_top_ips(self, date):
        """
        Возвращает топ IP адресов по количеству запросов
        """
        try:
            top_ips = []
            for key in cache.keys(f"ai_requests_ip_*_{date}"):
                ip = key.split('_')[3]
                count = cache.get(key, 0)
                top_ips.append({'ip': ip, 'requests': count})

            return sorted(top_ips, key=lambda x: x['requests'], reverse=True)[:10]
        except Exception:
            return []


# Глобальный экземпляр сервиса мониторинга
ai_monitor = AIMonitoringService()


class AIMonitoringMiddleware:
    """
    Middleware для автоматического мониторинга AI запросов
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Добавляем мониторинг в request object
        request.ai_monitor = ai_monitor

        response = self.get_response(request)

        return response