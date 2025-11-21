"""
🏗️ DI Container - Контейнер внедрения зависимостей для ИИ консультанта
Позволяет управлять жизненным циклом сервисов и внедрять зависимости
"""

import threading
from typing import Dict, Any, Optional, Type, TypeVar, Callable
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')

class DIContainer:
    """
    🔧 Простой DI контейнер для управления зависимостями
    """

    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable[[], Any]] = {}
        self._singletons: Dict[str, Any] = {}
        self._lock = threading.Lock()

    def register_singleton(self, interface_name: str, implementation: Type[T]) -> None:
        """
        Зарегистрировать singleton сервис

        Args:
            interface_name: Имя интерфейса/сервиса
            implementation: Класс реализации
        """
        with self._lock:
            self._factories[interface_name] = lambda: implementation()
            logger.info(f"Registered singleton: {interface_name} -> {implementation.__name__}")

    def register_factory(self, interface_name: str, factory: Callable[[], T]) -> None:
        """
        Зарегистрировать фабрику сервиса

        Args:
            interface_name: Имя интерфейса/сервиса
            factory: Фабричная функция
        """
        with self._lock:
            self._factories[interface_name] = factory
            logger.info(f"Registered factory: {interface_name}")

    def register_instance(self, interface_name: str, instance: T) -> None:
        """
        Зарегистрировать готовый экземпляр

        Args:
            interface_name: Имя интерфейса/сервиса
            instance: Готовый экземпляр
        """
        with self._lock:
            self._singletons[interface_name] = instance
            logger.info(f"Registered instance: {interface_name}")

    def get(self, interface_name: str) -> Any:
        """
        Получить экземпляр сервиса

        Args:
            interface_name: Имя интерфейса/сервиса

        Returns:
            Экземпляр сервиса

        Raises:
            KeyError: Если сервис не зарегистрирован
        """
        with self._lock:
            # Сначала проверяем синглтоны
            if interface_name in self._singletons:
                return self._singletons[interface_name]

            # Затем проверяем фабрики
            if interface_name in self._factories:
                if interface_name not in self._singletons:
                    # Создаем singleton при первом обращении
                    try:
                        instance = self._factories[interface_name]()
                        self._singletons[interface_name] = instance
                        logger.info(f"Created singleton instance: {interface_name}")
                    except Exception as e:
                        logger.error(f"Failed to create instance {interface_name}: {e}")
                        raise

                return self._singletons[interface_name]

            raise KeyError(f"Service '{interface_name}' not registered")

    def has(self, interface_name: str) -> bool:
        """
        Проверить, зарегистрирован ли сервис

        Args:
            interface_name: Имя интерфейса/сервиса

        Returns:
            True если сервис зарегистрирован
        """
        with self._lock:
            return interface_name in self._factories or interface_name in self._singletons

    def clear(self) -> None:
        """Очистить контейнер (полезно для тестов)"""
        with self._lock:
            self._services.clear()
            self._factories.clear()
            self._singletons.clear()
            logger.info("DI Container cleared")


# Глобальный контейнер
_container = DIContainer()

def get_container() -> DIContainer:
    """Получить глобальный DI контейнер"""
    return _container

def configure_services() -> None:
    """
    🔧 Конфигурация всех сервисов ИИ консультанта
    Регистрирует все зависимости в DI контейнере
    """
    container = get_container()

    try:
        # Импорты здесь чтобы избежать циклических зависимостей
        from ai_club_creator import AIClubCreator

        # Регистрируем AI Club Creator как singleton
        container.register_singleton('club_creator', AIClubCreator)

        # В будущем сюда можно добавить другие сервисы
        # container.register_singleton('conversation_service', ConversationService)
        # container.register_singleton('security_service', SecurityService)

        logger.info("✅ DI Container configured successfully")

    except Exception as e:
        logger.error(f"❌ Failed to configure DI container: {e}")
        raise

def get_service(service_name: str) -> Any:
    """
    Удобная функция для получения сервиса

    Args:
        service_name: Имя сервиса

    Returns:
        Экземпляр сервиса
    """
    return get_container().get(service_name)

# Автоматически конфигурируем сервисы при импорте
try:
    configure_services()
except Exception as e:
    logger.warning(f"DI container auto-configuration failed: {e}")
    logger.warning("Services will need to be configured manually")

logger.info("🏗️ DI Container module loaded")