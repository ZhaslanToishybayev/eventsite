import logging
from typing import Any, Dict
from abc import ABC, abstractmethod

class BaseAIService(ABC):
    """
    Базовый абстрактный класс для всех AI сервисов
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def process(self, *args, **kwargs) -> Any:
        """Основной метод обработки"""
        pass

    def log_info(self, message: str, extra: Dict = None):
        """Логирование информационных сообщений"""
        self.logger.info(f"[{self.__class__.__name__}] {message}", extra=extra or {})

    def log_error(self, message: str, exc_info=True, extra: Dict = None):
        """Логирование ошибок"""
        self.logger.error(f"[{self.__class__.__name__}] {message}", exc_info=exc_info, extra=extra or {})

    def get_cache_key(self, *args) -> str:
        """Генерация ключа кэша"""
        prefix = self.__class__.__name__.lower()
        key_parts = [str(arg) for arg in args]
        return f"{prefix}:{'_'.join(key_parts)}"
