"""
Advanced Redis caching system with multiple strategies
"""

import json
import pickle
import logging
from datetime import timedelta, datetime
from django.core.cache import cache
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
import redis
from typing import Any, Optional, Dict, List

logger = logging.getLogger(__name__)


class RedisManager:
    """
    Enhanced Redis manager with multiple cache strategies
    """

    def __init__(self):
        self.redis_client = self._get_redis_client()
        self.default_timeout = 300  # 5 минут

    def _get_redis_client(self):
        """
        Получаем Redis клиент с настройками
        """
        try:
            return redis.Redis(
                host=getattr(settings, 'REDIS_HOST', 'localhost'),
                port=int(getattr(settings, 'REDIS_PORT', 6379)),
                db=int(getattr(settings, 'REDIS_DB', 0)),
                password=getattr(settings, 'REDIS_PASSWORD', None),
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30,
                decode_responses=True
            )
        except Exception as e:
            logger.error(f"Redis connection error: {e}")
            return None

    def is_available(self) -> bool:
        """
        Проверяем доступность Redis
        """
        try:
            if self.redis_client:
                self.redis_client.ping()
                return True
        except Exception as e:
            logger.warning(f"Redis not available: {e}")
        return False

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Получаем статистику Redis
        """
        try:
            if not self.is_available():
                return {}

            info = self.redis_client.info()
            return {
                'used_memory': info.get('used_memory_human', 'N/A'),
                'used_memory_rss': info.get('used_memory_rss_human', 'N/A'),
                'connected_clients': info.get('connected_clients', 0),
                'total_commands_processed': info.get('total_commands_processed', 0),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'hit_rate': self._calculate_hit_rate(info)
            }
        except Exception as e:
            logger.error(f"Error getting Redis stats: {e}")
            return {}

    def _calculate_hit_rate(self, info: Dict) -> float:
        """
        Рассчитываем hit rate
        """
        hits = info.get('keyspace_hits', 0)
        misses = info.get('keyspace_misses', 0)
        total = hits + misses
        return (hits / total * 100) if total > 0 else 0.0

    def smart_cache(self, key: str, value: Any, timeout: Optional[int] = None, strategy: str = 'default'):
        """
        Умное кэширование с разными стратегиями
        """
        try:
            if not self.is_available():
                return False

            timeout = timeout or self.default_timeout
            cache_key = self._build_cache_key(key, strategy)

            if strategy == 'json':
                # Для JSON данных
                serialized_value = json.dumps(value, cls=DjangoJSONEncoder)
                return self.redis_client.setex(cache_key, timeout, serialized_value)

            elif strategy == 'pickle':
                # Для сложных объектов
                serialized_value = pickle.dumps(value)
                return self.redis_client.setex(cache_key, timeout, serialized_value)

            else:
                # Стандартное кэширование Django
                return cache.set(cache_key, value, timeout)

        except Exception as e:
            logger.error(f"Error caching key {key}: {e}")
            return False

    def smart_get(self, key: str, strategy: str = 'default', default: Any = None) -> Any:
        """
        Умное получение из кэша
        """
        try:
            if not self.is_available():
                return default

            cache_key = self._build_cache_key(key, strategy)

            if strategy == 'json':
                value = self.redis_client.get(cache_key)
                return json.loads(value) if value else default

            elif strategy == 'pickle':
                value = self.redis_client.get(cache_key)
                return pickle.loads(value) if value else default

            else:
                return cache.get(cache_key, default)

        except Exception as e:
            logger.error(f"Error getting cached key {key}: {e}")
            return default

    def invalidate_pattern(self, pattern: str) -> bool:
        """
        Инвалидируем кэш по шаблону
        """
        try:
            if not self.is_available():
                return False

            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
                logger.info(f"Invalidated {len(keys)} cache keys matching pattern: {pattern}")
                return True
            return False

        except Exception as e:
            logger.error(f"Error invalidating pattern {pattern}: {e}")
            return False

    def _build_cache_key(self, key: str, strategy: str) -> str:
        """
        Строим ключ кэша с префиксом и стратегией
        """
        prefix = getattr(settings, 'CACHE_KEY_PREFIX', 'unitysphere')
        return f"{prefix}:{strategy}:{key}"

    def warm_up_cache(self) -> bool:
        """
        Прогрев кэша для часто используемых данных
        """
        try:
            from clubs.models import Club
            from ai_consultant.models import DevelopmentPath

            if not self.is_available():
                return False

            # Прогрев популярных клубов
            popular_clubs = Club.objects.filter(
                is_active=True,
                members_count__gt=10
            ).select_related('category').order_by('-members_count')[:50]

            for club in popular_clubs:
                cache_key = f"club_detail_{club.id}"
                club_data = {
                    'id': str(club.id),
                    'name': club.name,
                    'members_count': club.members_count,
                    'category': str(club.category.name) if club.category else None
                }
                self.smart_cache(cache_key, club_data, timeout=3600, strategy='json')

            # Прогрев дорожек развития
            development_paths = DevelopmentPath.objects.filter(
                is_active=True
            ).prefetch_related('skills')[:20]

            for path in development_paths:
                cache_key = f"dev_path_{path.id}"
                path_data = {
                    'id': str(path.id),
                    'title': path.title,
                    'skills_count': path.skills.count()
                }
                self.smart_cache(cache_key, path_data, timeout=7200, strategy='json')

            logger.info("Cache warmed up successfully")
            return True

        except Exception as e:
            logger.error(f"Error warming up cache: {e}")
            return False


class CacheStrategies:
    """
    Предопределенные стратегии кэширования
    """

    @staticmethod
    def club_detail(club_id: int) -> str:
        """Кэш детальной страницы клуба"""
        return f"club:detail:{club_id}"

    @staticmethod
    def club_list(category_id: Optional[int] = None) -> str:
        """Кэш списка клубов"""
        return f"club:list:{category_id or 'all'}"

    @staticmethod
    def user_profile(user_id: int) -> str:
        """Кэш профиля пользователя"""
        return f"user:profile:{user_id}"

    @staticmethod
    def ai_response(message_hash: str) -> str:
        """Кэш AI ответов"""
        return f"ai:response:{message_hash}"

    @staticmethod
    def search_results(query_hash: str) -> str:
        """Кэш результатов поиска"""
        return f"search:results:{query_hash}"

    @staticmethod
    def recommendations(user_id: int) -> str:
        """Кэш рекомендаций"""
        return f"recommendations:user:{user_id}"


class CacheWarmer:
    """
    Автоматический прогрев кэша
    """

    def __init__(self):
        self.redis_manager = RedisManager()

    def warm_all(self):
        """
        Прогрев всех типов кэша
        """
        self.warm_clubs_cache()
        self.warm_ai_cache()
        self.warm_user_cache()

    def warm_clubs_cache(self):
        """Прогрев кэша клубов"""
        try:
            from clubs.models import Club, ClubCategory

            # Кэш категорий
            categories = ClubCategory.objects.filter(is_active=True)
            self.redis_manager.smart_cache(
                'club_categories',
                [{'id': str(c.id), 'name': c.name} for c in categories],
                timeout=86400,  # 24 часа
                strategy='json'
            )

            # Кэш популярных клубов
            popular_clubs = Club.objects.filter(
                is_active=True,
                members_count__gt=5
            ).order_by('-members_count')[:20]

            clubs_data = []
            for club in popular_clubs:
                clubs_data.append({
                    'id': str(club.id),
                    'name': club.name,
                    'category': str(club.category.name) if club.category else None,
                    'members_count': club.members_count
                })

            self.redis_manager.smart_cache(
                'popular_clubs',
                clubs_data,
                timeout=3600,  # 1 час
                strategy='json'
            )

            logger.info("Clubs cache warmed successfully")

        except Exception as e:
            logger.error(f"Error warming clubs cache: {e}")

    def warm_ai_cache(self):
        """Прогрев AI кэша"""
        try:
            # Кэш приветственных сообщений
            welcome_data = {
                'message': "🎉 Добро пожаловать в 'ЦЕНТР СОБЫТИЙ'!",
                'suggestions': [
                    'Расскажи о платформе "ЦЕНТР СОБЫТИЙ"',
                    'Какие клубы здесь есть?',
                    'Как создать свой клуб?'
                ]
            }

            self.redis_manager.smart_cache(
                'ai_welcome_message',
                welcome_data,
                timeout=86400,
                strategy='json'
            )

            logger.info("AI cache warmed successfully")

        except Exception as e:
            logger.error(f"Error warming AI cache: {e}")

    def warm_user_cache(self):
        """Прогрев кэша пользователей"""
        # Этот метод может быть расширен по необходимости
        pass


# Глобальные экземпляры
redis_manager = RedisManager()
cache_warmer = CacheWarmer()


class CacheMiddleware:
    """
    Middleware для автоматического кэширования
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.redis_manager = redis_manager

    def __call__(self, request):
        # Прогрев кэша если Redis доступен
        if self.redis_manager.is_available():
            # Можно добавить логику автоматического прогрева
            pass

        response = self.get_response(request)

        return response


def invalidate_cache_on_model_change(model_class, instance_id):
    """
    Инвалидирует кэш при изменении модели
    """
    model_name = model_class._meta.model_name

    if model_name == 'club':
        redis_manager.invalidate_pattern(f"*club*{instance_id}*")
        redis_manager.invalidate_pattern("*club:list*")
        redis_manager.invalidate_pattern("*popular_clubs*")

    elif model_name == 'user':
        redis_manager.invalidate_pattern(f"*user*{instance_id}*")
        redis_manager.invalidate_pattern("*recommendations*")

    logger.info(f"Cache invalidated for {model_name} {instance_id}")


def get_cache_hit_rate() -> Dict[str, Any]:
    """
    Получаем статистику hit rate кэша
    """
    stats = redis_manager.get_cache_stats()
    return {
        'redis_available': redis_manager.is_available(),
        'hit_rate': stats.get('hit_rate', 0),
        'used_memory': stats.get('used_memory', 'N/A'),
        'connected_clients': stats.get('connected_clients', 0),
        'timestamp': datetime.now().isoformat()
    }