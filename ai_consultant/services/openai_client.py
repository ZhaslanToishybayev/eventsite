"""
🤖 OpenAI клиент сервис v2.0
Оптимизированная работа с OpenAI API
"""

import logging
from typing import Dict, Any, Optional, List
from django.conf import settings
from openai import OpenAI
from django.core.cache import cache
import json

from .base import BaseAIService


class OpenAIClientService(BaseAIService):
    """
    Сервис для работы с OpenAI API
    """

    def __init__(self):
        super().__init__()
        self.client = None
        self.model = getattr(settings, 'OPENAI_MODEL', 'gpt-3.5-turbo')
        self.max_tokens = getattr(settings, 'OPENAI_MAX_TOKENS', 1000)
        self.temperature = getattr(settings, 'OPENAI_TEMPERATURE', 0.7)
        self.timeout = getattr(settings, 'OPENAI_TIMEOUT', 30)
        self._initialize_client()

    def _initialize_client(self):
        """Инициализация OpenAI клиента"""
        try:
            api_key = getattr(settings, 'OPENAI_API_KEY', None)
            if not api_key:
                self.log_error("OpenAI API ключ не настроен")
                return

            self.client = OpenAI(api_key=api_key)
            self.log_info("OpenAI клиент инициализирован")

        except Exception as e:
            self.log_error(f"Ошибка инициализации OpenAI клиента: {e}")
            self.client = None

    def process(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        Основной метод обработки сообщений
        """
        return self.chat_completion(messages, **kwargs)

    def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        Выполняет запрос к OpenAI Chat Completion
        """
        if not self.is_available():
            return self._get_error_response("OpenAI сервис недоступен")

        try:
            # Проверяем кэш для одинаковых запросов
            cache_key = self._get_cache_key_for_messages(messages)
            cached_response = cache.get(cache_key)
            if cached_response:
                self.log_info("Ответ загружен из кэша")
                return cached_response

            # Подготовка параметров запроса
            params = {
                'model': kwargs.get('model', self.model),
                'messages': messages,
                'max_tokens': kwargs.get('max_tokens', self.max_tokens),
                'temperature': kwargs.get('temperature', self.temperature),
            }
            
            # Add tools if provided
            if 'tools' in kwargs and kwargs['tools']:
                params['tools'] = kwargs['tools']
                if 'tool_choice' in kwargs and kwargs['tool_choice']:
                    params['tool_choice'] = kwargs['tool_choice']
            
            # Add response_format if provided
            if 'response_format' in kwargs:
                params['response_format'] = kwargs['response_format']

            # Выполнение запроса
            try:
                response = self.client.chat.completions.create(**params)
            except Exception as api_error:
                error_msg = str(api_error)
                self.log_error(f"OpenAI API error: {error_msg}")
                
                # Check if it's the empty response error
                if "empty" in error_msg.lower() or "must contain either" in error_msg.lower():
                    # Return a simple text response as fallback
                    return {
                        'content': "Привет! Чем могу помочь? 🌟",
                        'role': 'assistant',
                        'finish_reason': 'fallback',
                        'tokens_used': 0,
                        'model': params['model'],
                        'success': True,
                        'fallback': True
                    }
                
                # For other errors, return error response
                return self._get_error_response(f"API Error: {error_msg}")

            # Обработка ответа
            result = self._process_response(response)

            # Кэширование результата (только если нет tool_calls)
            if not result.get('tool_calls'):
                cache_timeout = getattr(settings, 'AI_RESPONSE_CACHE_TIMEOUT', 300)
                cache.set(cache_key, result, cache_timeout)

            self.log_info("Chat completion выполнен успешно", {
                'model': params['model'],
                'tokens_used': result.get('tokens_used', 0),
                'has_tool_calls': bool(result.get('tool_calls'))
            })

            return result

        except Exception as e:
            self.log_error(f"Ошибка chat completion: {e}")
            return self._get_error_response(f"Ошибка API: {str(e)}")

    def chat_completion_stream(self, messages: List[Dict[str, str]], **kwargs):
        """
        Выполняет streaming запрос к OpenAI Chat Completion
        """
        if not self.is_available():
            yield "OpenAI сервис недоступен"
            return

        try:
            params = {
                'model': kwargs.get('model', self.model),
                'messages': messages,
                'max_tokens': kwargs.get('max_tokens', self.max_tokens),
                'temperature': kwargs.get('temperature', self.temperature),
                'stream': True
            }

            response = self.client.chat.completions.create(**params)

            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            self.log_error(f"Ошибка chat completion stream: {e}")
            yield f"Ошибка: {str(e)}"

    def simple_completion(self, prompt: str, **kwargs) -> str:
        """
        Простое завершение текста
        """
        messages = [{"role": "user", "content": prompt}]
        response = self.chat_completion(messages, **kwargs)
        return response.get('content', '')

    def is_available(self) -> bool:
        """
        Проверяет доступность OpenAI сервиса
        """
        return self.client is not None

    def get_models(self) -> List[str]:
        """
        Получает список доступных моделей
        """
        if not self.is_available():
            return []

        try:
            models = self.client.models.list()
            return [model.id for model in models.data]
        except Exception as e:
            self.log_error(f"Ошибка получения моделей: {e}")
            return []

    def estimate_tokens(self, text: str) -> int:
        """
        Оценивает количество токенов в тексте
        """
        # Простая оценка: ~4 символа = 1 токен
        return max(1, len(text) // 4)

    def truncate_messages(self, messages: List[Dict[str, str]], max_tokens: int = None) -> List[Dict[str, str]]:
        """
        Обрезает сообщения чтобы уложиться в лимит токенов
        """
        if max_tokens is None:
            max_tokens = self.max_tokens * 2  # Примерная оценка

        total_tokens = sum(self.estimate_tokens(msg.get('content', '')) for msg in messages)

        if total_tokens <= max_tokens:
            return messages

        # Оставляем системное сообщение и обрезаем историю
        system_messages = [msg for msg in messages if msg.get('role') == 'system']
        other_messages = [msg for msg in messages if msg.get('role') != 'system']

        # Обрезаем с конца (самые старые сообщения)
        tokens_used = sum(self.estimate_tokens(msg.get('content', '')) for msg in system_messages)

        truncated_messages = system_messages.copy()
        for msg in reversed(other_messages):
            msg_tokens = self.estimate_tokens(msg.get('content', ''))
            if tokens_used + msg_tokens <= max_tokens:
                truncated_messages.insert(len(system_messages), msg)
                tokens_used += msg_tokens
            else:
                break

        self.log_info(f"Сообщения обрезаны", {
            'original_count': len(messages),
            'truncated_count': len(truncated_messages),
            'tokens_saved': total_tokens - tokens_used
        })

        return truncated_messages

    def _process_response(self, response) -> Dict[str, Any]:
        """
        Обрабатывает ответ от OpenAI
        """
        try:
            choice = response.choices[0]
            message = choice.message
            content = message.content or ""  # Handle None content when tool_calls present

            # Получаем информацию об использовании токенов
            usage = getattr(response, 'usage', None)
            tokens_used = usage.total_tokens if usage else 0
            
            result = {
                'content': content.strip() if content else "",
                'role': message.role,
                'finish_reason': choice.finish_reason,
                'tokens_used': tokens_used,
                'model': response.model,
                'created': response.created,
                'success': True
            }
            
            # Add tool_calls if present
            if hasattr(message, 'tool_calls') and message.tool_calls:
                result['tool_calls'] = [
                    {
                        'id': tc.id,
                        'type': tc.type,
                        'function': {
                            'name': tc.function.name,
                            'arguments': tc.function.arguments
                        }
                    }
                    for tc in message.tool_calls
                ]

            return result

        except (IndexError, AttributeError) as e:
            self.log_error(f"Ошибка обработки ответа: {e}")
            return self._get_error_response("Некорректный ответ от API")

    def _get_error_response(self, error_message: str) -> Dict[str, Any]:
        """
        Возвращает ответ с ошибкой
        """
        return {
            'content': '',
            'role': 'assistant',
            'finish_reason': 'error',
            'tokens_used': 0,
            'model': self.model,
            'error': error_message,
            'success': False
        }

    def _get_cache_key_for_messages(self, messages: List[Dict[str, str]]) -> str:
        """
        Генерирует ключ кэша для сообщений
        """
        import hashlib
        messages_str = json.dumps(messages, sort_keys=True)
        hash_obj = hashlib.md5(messages_str.encode())
        return f"openai_response_{hash_obj.hexdigest()}"

    def health_check(self) -> bool:
        """
        Проверка работоспособности сервиса
        """
        if not self.is_available():
            return False

        try:
            # Пробуем выполнить простой запрос
            test_response = self.simple_completion("Say 'test'", max_tokens=5)
            return bool(test_response and 'test' in test_response.lower())
        except Exception as e:
            self.log_error(f"Health check не пройден: {e}")
            return False

    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Получает статистику использования (заглушка)
        """
        # В реальном приложении здесь можно подключить API OpenAI для статистики
        return {
            'model': self.model,
            'max_tokens': self.max_tokens,
            'temperature': self.temperature,
            'available': self.is_available()
        }

    def cleanup(self):
        """
        Очистка ресурсов
        """
        if self.client:
            self.client.close()
            self.client = None
        self.log_info("OpenAI клиент очищен")