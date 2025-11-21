"""
Сервис для интеграции Serena AI с UnitySphere
"""
import requests
import json
import logging
from typing import Dict, Optional, Any
from django.conf import settings

logger = logging.getLogger(__name__)


class SerenaAIService:
    """
    Сервис для работы с Serena AI через MCP протокол
    """

    def __init__(self):
        self.serena_url = getattr(settings, 'SERENA_URL', 'http://localhost:8001')
        self.timeout = 30

    def health_check(self) -> bool:
        """Проверка доступности Serena"""
        try:
            response = requests.get(f"{self.serena_url}/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Serena health check failed: {e}")
            return False

    def send_request(self, method: str, params: Dict[str, Any] = None) -> Optional[Dict]:
        """Отправка запроса к Serena"""
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": method,
                "params": params or {}
            }

            response = requests.post(
                f"{self.serena_url}/mcp",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=self.timeout
            )

            if response.status_code == 200:
                result = response.json()
                if 'result' in result:
                    return result['result']
                elif 'error' in result:
                    logger.error(f"Serena error: {result['error']}")
                    return None
            else:
                logger.error(f"Serena request failed: {response.status_code}")

        except Exception as e:
            logger.error(f"Serena request exception: {e}")

        return None

    def get_project_info(self) -> Optional[Dict]:
        """Получить информацию о проекте"""
        return self.send_request("get_current_config")

    def find_symbol(self, symbol_name: str, relative_path: str = None) -> Optional[Dict]:
        """Найти символ в коде"""
        params = {"symbol_name": symbol_name}
        if relative_path:
            params["relative_path"] = relative_path
        return self.send_request("tools/call", {
            "name": "find_symbol",
            "arguments": params
        })

    def read_file(self, relative_path: str) -> Optional[str]:
        """Прочитать файл проекта"""
        result = self.send_request("tools/call", {
            "name": "read_file",
            "arguments": {"relative_path": relative_path}
        })
        return result.get('content') if result else None

    def get_symbols_overview(self, relative_path: str) -> Optional[Dict]:
        """Получить обзор символов в файле"""
        result = self.send_request("tools/call", {
            "name": "get_symbols_overview",
            "arguments": {"relative_path": relative_path}
        })
        return result

    def search_for_pattern(self, pattern: str, relative_path: str = None) -> Optional[Dict]:
        """Поиск паттерна в коде"""
        params = {"pattern": pattern}
        if relative_path:
            params["relative_path"] = relative_path
        return self.send_request("tools/call", {
            "name": "search_for_pattern",
            "arguments": params
        })

    def create_code_improvement_suggestion(self, file_path: str, issue_description: str) -> Optional[str]:
        """Получить предложение по улучшению кода"""
        # Используем Serena для анализа кода и предложений
        try:
            # Читаем файл
            file_content = self.read_file(file_path)
            if not file_content:
                return None

            # Получаем обзор символов
            symbols = self.get_symbols_overview(file_path)

            # Формируем запрос к Serena для анализа
            analysis_prompt = f"""
            Проанализируй следующий код и предложи улучшения для решения проблемы: {issue_description}

            Файл: {file_path}

            Символы в файле:
            {json.dumps(symbols, indent=2, ensure_ascii=False) if symbols else 'Нет символов'}

            Код:
            {file_content[:2000]}...  # Первые 2000 символов для анализа

            Предложи конкретные улучшения с объяснениями.
            """

            # Здесь можно интегрировать с дополнительным ИИ для анализа
            # или использовать встроенные возможности Serena

            return f"""
            🔍 **Анализ кода для {file_path}**

            📋 **Найденные символы:** {len(symbols.get('symbols', [])) if symbols else 0}

            💡 **Предложения по улучшению для:** {issue_description}

            🛠️ **Рекомендации:**
            • Проверить стиль кода (PEP 8)
            • Оптимизировать производительность
            • Улучшить читаемость
            • Добавить документацию

            📝 **Дальнейшие шаги:**
            1. Изучить структуру файла
            2. Применить лучшие практики Django
            3. Добавить тесты если необходимо
            """

        except Exception as e:
            logger.error(f"Code improvement analysis failed: {e}")
            return None

    def explain_code_structure(self, file_path: str) -> Optional[str]:
        """Объяснить структуру кода в файле"""
        try:
            # Получаем обзор символов
            symbols = self.get_symbols_overview(file_path)
            if not symbols:
                return "Не удалось получить информацию о файле"

            # Читаем начало файла
            file_content = self.read_file(file_path)
            if not file_content:
                return "Не удалось прочитать файл"

            # Анализируем структуру
            lines = file_content.split('\n')[:50]  # Первые 50 строк
            imports = [line for line in lines if line.strip().startswith(('import', 'from'))]
            classes = [s for s in symbols.get('symbols', []) if s.get('kind') == 'class']
            functions = [s for s in symbols.get('symbols', []) if s.get('kind') == 'function']

            explanation = f"""
            📁 **Структура файла:** {file_path}

            📦 **Импорты ({len(imports)}):**
            {chr(10).join(f"• {imp.strip()}" for imp in imports[:5])}
            {f"... и ещё {len(imports)-5}" if len(imports) > 5 else ""}

            🏗️ **Классы ({len(classes)}):**
            {chr(10).join(f"• {cls.get('name', 'Unknown')}" for cls in classes[:5])}
            {f"... и ещё {len(classes)-5}" if len(classes) > 5 else ""}

            🔧 **Функции ({len(functions)}):**
            {chr(10).join(f"• {func.get('name', 'Unknown')}" for func in functions[:5])}
            {f"... и ещё {len(functions)-5}" if len(functions) > 5 else ""}

            📝 **Назначение файла:**
            """

            # Добавляем базовое определение типа файла
            if 'models' in file_path:
                explanation += "Модели данных Django"
            elif 'views' in file_path:
                explanation += "Представления Django (View)"
            elif 'serializers' in file_path:
                explanation += "Сериализаторы Django REST"
            elif 'urls' in file_path:
                explanation += "URL маршрутизация"
            elif 'forms' in file_path:
                explanation += "Формы Django"
            elif 'admin' in file_path:
                explanation += "Административная панель"
            elif 'tests' in file_path:
                explanation += "Тесты"
            elif 'migrations' in file_path:
                explanation += "Миграции базы данных"
            else:
                explanation += "Вспомогательный модуль"

            return explanation

        except Exception as e:
            logger.error(f"Code structure analysis failed: {e}")
            return "Не удалось проанализировать структуру кода"

    def generate_documentation(self, file_path: str) -> Optional[str]:
        """Сгенерировать документацию для файла"""
        try:
            # Анализируем файл
            structure = self.explain_code_structure(file_path)
            symbols = self.get_symbols_overview(file_path)

            if not symbols:
                return None

            doc = f"""
            # 📚 Документация: {file_path}

            {structure}

            """

            # Добавляем документацию для классов
            classes = [s for s in symbols.get('symbols', []) if s.get('kind') == 'class']
            for cls in classes[:3]:  # Первые 3 класса
                doc += f"""
            ## 🏗️ Класс: {cls.get('name', 'Unknown')}

            **Тип:** {cls.get('kind', 'Unknown')}
            **Расположение:** строки {cls.get('range', {}).get('start', 'N/A')}

            """

                # Добавляем методы класса
                methods = [s for s in symbols.get('symbols', [])
                         if s.get('kind') == 'function' and s.get('name_path', '').startswith(f"{cls.get('name', '')}/")]

                if methods:
                    doc += "**Методы:**\n"
                    for method in methods[:5]:
                        doc += f"• `{method.get('name', 'Unknown')}`\n"

            # Добавляем документацию для функций
            functions = [s for s in symbols.get('symbols', []) if s.get('kind') == 'function']
            if functions:
                doc += "\n## 🔧 Функции\n"
                for func in functions[:5]:
                    doc += f"• `{func.get('name', 'Unknown')}`\n"

            return doc

        except Exception as e:
            logger.error(f"Documentation generation failed: {e}")
            return None