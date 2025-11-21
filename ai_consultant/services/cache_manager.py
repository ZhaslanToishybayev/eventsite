import hashlib
from django.core.cache import cache
from django.conf import settings
from typing import Optional

class ResponseCacheManager:
    """
    Менеджер кэширования ответов AI для оптимизации расходов и ускорения работы
    """
    
    CACHE_TTL = getattr(settings, 'AI_RESPONSE_CACHE_TTL', 3600)  # 1 час по умолчанию
    CACHE_PREFIX = "ai_response"
    
    @staticmethod
    def _generate_hash(content: str) -> str:
        """Генерация хеша для контента"""
        return hashlib.sha256(content.encode()).hexdigest()
    
    def get_cache_key(self, message: str, context_hash: str = "") -> str:
        """Формирование ключа кэша"""
        message_hash = self._generate_hash(message.strip().lower())
        return f"{self.CACHE_PREFIX}:{message_hash}:{context_hash}"
    
    def get_cached_response(self, message: str, context_hash: str = "") -> Optional[str]:
        """Получение ответа из кэша"""
        key = self.get_cache_key(message, context_hash)
        return cache.get(key)
    
    def cache_response(self, message: str, response: str, context_hash: str = ""):
        """Сохранение ответа в кэш"""
        key = self.get_cache_key(message, context_hash)
        cache.set(key, response, self.CACHE_TTL)
        
    def clear_cache(self, message: str, context_hash: str = ""):
        """Очистка кэша для конкретного сообщения"""
        key = self.get_cache_key(message, context_hash)
        cache.delete(key)
