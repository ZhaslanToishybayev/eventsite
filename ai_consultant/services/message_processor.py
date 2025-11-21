"""
📨 Процессор сообщений v2.0
Предварительная и постобработка сообщений
"""

import re
import logging
from typing import Dict, Any, List, Optional
from html import escape
from django.utils.html import strip_tags

from .base import BaseAIService


class MessageProcessorService(BaseAIService):
    """
    Сервис для обработки и форматирования сообщений
    """

    def __init__(self):
        super().__init__()
        self.max_message_length = 2000
        self.min_message_length = 1

        # Паттерны для очистки текста
        self.dangerous_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'eval\s*\(',
            r'alert\s*\(',
            r'document\.cookie',
            r'window\.',
            r'document\.',
        ]

        # Эмодзи для замены
        self.emoji_replacements = {
            ':)': '😊',
            ':-)': '😊',
            ':(': '😢',
            ':-(': '😢',
            ':D': '😃',
            ':-D': '😃',
            ':P': '😛',
            ':-P': '😛',
            ':O': '😮',
            ':-O': '😮',
            ';)': '😉',
            ';-)': '😉',
            ':heart:': '❤️',
            '<3': '❤️',
            ':thumbs_up:': '👍',
            ':fire:': '🔥',
            ':rocket:': '🚀',
            ':star:': '⭐',
            ':check:': '✅',
            ':error:': '❌',
            ':warning:': '⚠️',
            ':info:': 'ℹ️',
        }

    def process(self, message: str, action: str = 'preprocess', **kwargs) -> str:
        """
        Основной метод обработки сообщений
        """
        if action == 'preprocess':
            return self.preprocess(message)
        elif action == 'postprocess':
            return self.postprocess(message)
        else:
            return message

    def preprocess(self, message: str) -> str:
        """
        Предварительная обработка входящего сообщения
        """
        try:
            if not message:
                raise ValueError("Сообщение не может быть пустым")

            # Базовая очистка
            processed = self._basic_cleanup(message)

            # Валидация длины
            self._validate_length(processed)

            # Очистка от опасного контента
            processed = self._remove_dangerous_content(processed)

            # Нормализация пробелов
            processed = self._normalize_whitespace(processed)

            # Замена текстовых эмодзи
            processed = self._replace_text_emojis(processed)

            # Финальная проверка
            self._final_validation(processed)

            self.log_info(f"Сообщение предобработано", {
                'original_length': len(message),
                'processed_length': len(processed)
            })

            return processed.strip()

        except ValueError as e:
            self.log_error(f"Ошибка валидации сообщения: {e}")
            raise
        except Exception as e:
            self.log_error(f"Ошибка предобработки сообщения: {e}")
            return message  # Возвращаем оригинал в случае ошибки

    def postprocess(self, message: str) -> str:
        """
        Постобработка ответа от ИИ
        Возвращает чистый текст без HTML - виджет сам форматирует
        """
        try:
            if not message:
                return ""

            # Просто возвращаем оригинальное сообщение
            # Виджет сам обработает markdown и эмодзи
            return message.strip()

        except Exception as e:
            self.log_error(f"Ошибка постобработки сообщения: {e}")
            return message  # Возвращаем оригинал в случае ошибки

    def extract_keywords(self, message: str, limit: int = 10) -> List[str]:
        """
        Извлекает ключевые слова из сообщения
        """
        try:
            # Удаляем знаки препинания и приводим к нижнему регистру
            words = re.findall(r'\b\w+\b', message.lower())

            # Фильтруем стоп-слова
            stop_words = {
                'и', 'в', 'на', 'с', 'по', 'для', 'о', 'об', 'от', 'к', 'у', 'из', 'без', 'до', 'во',
                'что', 'как', 'где', 'когда', 'почему', 'зачем', 'сколько', 'чей', 'какой',
                'это', 'тот', 'этот', 'такой', 'столько', 'там', 'здесь', 'туда', 'сюда',
                'быть', 'может', 'может быть', 'хочу', 'хотел', 'хотела', 'нужно', 'надо'
            }

            # Фильтруем и считаем частоту
            filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
            word_count = {}
            for word in filtered_words:
                word_count[word] = word_count.get(word, 0) + 1

            # Сортируем по частоте и возвращаем топ-N
            keywords = sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:limit]

            return [keyword for keyword, count in keywords]

        except Exception as e:
            self.log_error(f"Ошибка извлечения ключевых слов: {e}")
            return []

    def detect_intent(self, message: str) -> Dict[str, Any]:
        """
        Определяет намерение пользователя
        """
        try:
            message_lower = message.lower()

            # Паттерны для определения намерений
            intent_patterns = {
                'question': [
                    r'\?', r'как', r'что', r'где', r'когда', r'почему', r'зачем',
                    r'объясни', r'расскажи', r'покажи', r'помоги'
                ],
                'club_creation': [
                    r'создать клуб', r'новый клуб', r'как создать', r'открыть клуб',
                    r'создание клуба', r'клуб создание'
                ],
                'search': [
                    r'найди', r'поиск', r'ищу', r'подскажи', r'где найти',
                    r'покажи клубы', r'список клубов'
                ],
                'help': [
                    r'помощь', r'помоги', r'не работает', r'проблема', r'ошибка',
                    r'как пользоваться', r'инструкция'
                ],
                'greeting': [
                    r'привет', r'здравствуй', r'добрый день', r'хай', r'хеллоу'
                ],
                'farewell': [
                    r'пока', r'до свидания', r'до встречи', r'спасибо', r'благодарю'
                ]
            }

            # Определяем намерения
            detected_intents = {}
            for intent, patterns in intent_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, message_lower):
                        detected_intents[intent] = True
                        break

            # Извлекаем ключевые слова
            keywords = self.extract_keywords(message, 5)

            # Определяем эмоциональную окраску
            sentiment = self._detect_sentiment(message_lower)

            result = {
                'intents': list(detected_intents.keys()),
                'primary_intent': self._get_primary_intent(detected_intents),
                'keywords': keywords,
                'sentiment': sentiment,
                'message_length': len(message),
                'has_question': '?' in message
            }

            self.log_info(f"Намерение определено", {
                'intents': result['intents'],
                'primary_intent': result['primary_intent'],
                'sentiment': result['sentiment']
            })

            return result

        except Exception as e:
            self.log_error(f"Ошибка определения намерения: {e}")
            return {'intents': [], 'primary_intent': 'unknown', 'keywords': [], 'sentiment': 'neutral'}

    def format_for_display(self, message: str, is_from_user: bool = False) -> str:
        """
        Форматирует сообщение для отображения в интерфейсе
        """
        try:
            if is_from_user:
                # Для сообщений пользователя просто экранируем HTML
                return escape(message)
            else:
                # Для сообщений ИИ применяем полное форматирование
                return self.postprocess(message)

        except Exception as e:
            self.log_error(f"Ошибка форматирования для отображения: {e}")
            return escape(message)

    # Приватные методы

    def _basic_cleanup(self, message: str) -> str:
        """Базовая очистка текста"""
        # Удаляем HTML теги
        cleaned = strip_tags(message)
        # Удаляем лишние пробелы
        cleaned = re.sub(r'\s+', ' ', cleaned)
        return cleaned

    def _validate_length(self, message: str):
        """Валидация длины сообщения"""
        length = len(message.strip())
        if length < self.min_message_length:
            raise ValueError(f"Сообщение слишком короткое (минимум {self.min_message_length} символа)")
        if length > self.max_message_length:
            raise ValueError(f"Сообщение слишком длинное (максимум {self.max_message_length} символов)")

    def _remove_dangerous_content(self, message: str) -> str:
        """Удаляет потенциально опасный контент"""
        cleaned = message
        for pattern in self.dangerous_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        return cleaned

    def _normalize_whitespace(self, message: str) -> str:
        """Нормализация пробелов"""
        # Удаляем лишние пробелы
        return re.sub(r'\s+', ' ', message)

    def _replace_text_emojis(self, message: str) -> str:
        """Заменяет текстовые эмодзи на настоящие"""
        for text_emoji, emoji in self.emoji_replacements.items():
            message = message.replace(text_emoji, emoji)
        return message

    def _final_validation(self, message: str):
        """Финальная проверка сообщения"""
        if not message.strip():
            raise ValueError("Сообщение не может быть пустым после очистки")

    def _format_markdown(self, message: str) -> str:
        """Форматирует markdown элементы"""
        # Жирный текст
        message = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', message)
        # Курсив
        message = re.sub(r'\*(.*?)\*', r'<em>\1</em>', message)
        # Код
        message = re.sub(r'`(.*?)`', r'<code>\1</code>', message)
        # Заголовки
        message = re.sub(r'^### (.*)$', r'<h3>\1</h3>', message, flags=re.MULTILINE)
        message = re.sub(r'^## (.*)$', r'<h2>\1</h2>', message, flags=re.MULTILINE)
        message = re.sub(r'^# (.*)$', r'<h1>\1</h1>', message, flags=re.MULTILINE)
        return message

    def _format_emojis(self, message: str) -> str:
        """Форматирует эмодзи"""
        # Увеличиваем эмодзи для лучшей видимости
        return re.sub(r'([😀-🿿])', r'<span style="font-size: 1.2em;">\1</span>', message)

    def _format_links(self, message: str) -> str:
        """Форматирует ссылки"""
        # Сначала конвертируем абсолютные URL в относительные для локальных ссылок
        message = self._convert_absolute_to_relative(message)

        # HTTP/HTTPS ссылки
        url_pattern = r'(https?://[^\s<>"{}|\\^`\[\]]+)'
        message = re.sub(
            url_pattern,
            r'<a href="\1" target="_blank" rel="noopener noreferrer">\1</a>',
            message
        )
        return message

    def _convert_absolute_to_relative(self, message: str) -> str:
        """Конвертирует абсолютные URL локального сайта в относительные"""
        import re
        from django.conf import settings

        # Список доменов которые нужно конвертировать в относительные URL
        local_domains = [
            'localhost:8000',
            '127.0.0.1:8000',
            'centersobytij.com',
            'fan-club.kz',
            'www.fan-club.kz'
        ]

        # Создаем паттерн для поиска локальных URL
        domain_pattern = '|'.join([re.escape(domain) for domain in local_domains])
        url_pattern = f'https?://(?:{domain_pattern})(/[^\s<>"{{}}|\\^`\[\]]*)'

        def replace_relative(match):
            # Возвращаем только путь без домена
            relative_url = match.group(1)
            return relative_url

        # Заменяем абсолютные URL на относительные
        message = re.sub(url_pattern, replace_relative, message)

        return message

    def _format_lists(self, message: str) -> str:
        """Форматирует списки"""
        lines = message.split('\n')
        formatted_lines = []
        in_list = False

        for line in lines:
            # Маркированные списки
            if re.match(r'^[\*\-\+] +', line):
                if not in_list:
                    formatted_lines.append('<ul>')
                    in_list = True
                item = re.sub(r'^[\*\-\+] +', '', line)
                formatted_lines.append(f'<li>{item}</li>')
            # Нумерованные списки
            elif re.match(r'^\d+\. +', line):
                if not in_list:
                    formatted_lines.append('<ol>')
                    in_list = True
                item = re.sub(r'^\d+\. +', '', line)
                formatted_lines.append(f'<li>{item}</li>')
            else:
                if in_list:
                    formatted_lines.append('</ul>' if isinstance(formatted_lines[-1], str) and formatted_lines[-1].startswith('<li>') else '</ol>')
                    in_list = False
                formatted_lines.append(line)

        if in_list:
            formatted_lines.append('</ul>')

        return '\n'.join(formatted_lines)

    def _format_paragraphs(self, message: str) -> str:
        """Форматирует параграфы"""
        # Разделяем на параграфы по пустым строкам
        paragraphs = message.split('\n\n')
        formatted_paragraphs = []

        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if paragraph and not paragraph.startswith('<'):
                formatted_paragraphs.append(f'<p>{paragraph}</p>')
            else:
                formatted_paragraphs.append(paragraph)

        return '\n'.join(formatted_paragraphs)

    def _final_cleanup(self, message: str) -> str:
        """Финальная очистка"""
        # Удаляем пустые параграфы
        message = re.sub(r'<p>\s*</p>', '', message)
        # Удаляем лишние переносы
        message = re.sub(r'\n+', '\n', message)
        return message.strip()

    def _detect_sentiment(self, message: str) -> str:
        """Определяет эмоциональную окраску"""
        positive_words = ['хорошо', 'отлично', 'замечательно', 'прекрасно', 'спасибо', 'благодарю', 'рад', 'супер']
        negative_words = ['плохо', 'ужасно', 'терrible', 'проблема', 'ошибка', 'не работает', 'зло']

        positive_count = sum(1 for word in positive_words if word in message)
        negative_count = sum(1 for word in negative_words if word in message)

        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'

    def _get_primary_intent(self, intents: List[str]) -> str:
        """Определяет основное намерение"""
        intent_priority = {
            'greeting': 1,
            'farewell': 2,
            'help': 3,
            'question': 4,
            'search': 5,
            'club_creation': 6
        }

        if not intents:
            return 'unknown'

        # Возвращаем намерение с наивысшим приоритетом
        return min(intents, key=lambda x: intent_priority.get(x, 999))

    def health_check(self) -> bool:
        """Проверка работоспособности сервиса"""
        try:
            test_message = "Привет! Как дела?"
            processed = self.preprocess(test_message)
            postprocessed = self.postprocess(test_message)
            return bool(processed and postprocessed)
        except Exception as e:
            self.log_error(f"Health check не пройден: {e}")
            return False