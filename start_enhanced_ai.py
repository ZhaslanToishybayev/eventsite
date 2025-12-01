#!/usr/bin/env python3
"""
🚀 Enhanced AI Agent Server for UnitySphere
Улучшенная версия сервера с enhanced агентом
"""

import http.server
import socketserver
import json
import urllib.parse
import sys
import os
import threading
import time
from datetime import datetime

# Добавляем путь к модулям
sys.path.append('/var/www/myapp/eventsite/ai_consultant/agents')

try:
    from enhanced_production_agent import EnhancedAIConsultant, process_ai_message
    print("✅ Загружен EnhancedAIConsultant")
except ImportError as e:
    print(f"❌ Ошибка импорта EnhancedAIConsultant: {e}")
    # Резервная загрузка оригинального агента
    try:
        from lightweight_production_agent import LightweightAIConsultant
        print("✅ Загружен резервный LightweightAIConsultant")
        EnhancedAIConsultant = LightweightAIConsultant
        def process_ai_message(message, session_id="default", history=None):
            agent = EnhancedAIConsultant()
            return agent.process_message(message, session_id)
    except ImportError as e2:
        print(f"❌ Ошибка импорта резервного агента: {e2}")
        sys.exit(1)

class EnhancedAIHandler(http.server.BaseHTTPRequestHandler):
    """🤖 Обработчик запросов для улучшенного AI агента"""

    def __init__(self, *args, **kwargs):
        self.ai_agent = EnhancedAIConsultant()
        super().__init__(*args, **kwargs)

    def _set_cors_headers(self):
        """Устанавливаем CORS заголовки"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-CSRFToken')
        self.send_header('Access-Control-Max-Age', '86400')

    def do_OPTIONS(self):
        """Обработка OPTIONS запросов для CORS"""
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def do_GET(self):
        """Обработка GET запросов"""
        path = self.path

        if path == '/':
            self.send_response(200)
            self._set_cors_headers()
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            response = {
                "status": "healthy",
                "service": "Enhanced UnitySphere AI Agent",
                "version": "2.0.0",
                "features": [
                    "Natural language processing",
                    "Club creation workflow",
                    "Conversation history support",
                    "Enhanced validation",
                    "Smart intent recognition"
                ],
                "timestamp": datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(response, ensure_ascii=False, indent=2).encode())

        elif path == '/health':
            self.send_response(200)
            self._set_cors_headers()
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            response = {
                "status": "healthy",
                "ai_agent": "EnhancedAIConsultant",
                "timestamp": datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode())

        elif path == '/info':
            self.send_response(200)
            self._set_cors_headers()
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            response = {
                "service": "Enhanced UnitySphere AI Agent",
                "version": "2.0.0",
                "description": "Advanced AI consultant for club creation",
                "features": {
                    "natural_language": "Natural language understanding",
                    "conversation_history": "Maintains conversation context",
                    "intent_recognition": "Smart intent detection",
                    "validation": "Enhanced input validation",
                    "multi_language": "Russian language support",
                    "error_handling": "Robust error handling"
                },
                "endpoints": {
                    "/": "Service status and info",
                    "/health": "Health check",
                    "/info": "Service information",
                    "/api/agent": "AI conversation endpoint"
                }
            }
            self.wfile.write(json.dumps(response, ensure_ascii=False, indent=2).encode())

        else:
            self.send_response(404)
            self._set_cors_headers()
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"error": "Not found", "path": path}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode())

    def do_POST(self):
        """Обработка POST запросов"""
        path = self.path

        if path == '/api/agent' or path == '/':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)

            try:
                # Парсим JSON данные
                data = json.loads(post_data.decode('utf-8'))

                # Извлекаем данные
                message = data.get('message', '').strip()
                session_id = data.get('session_id', f"session_{int(time.time())}")
                history = data.get('history', [])

                print(f"📨 Received message: '{message}' from session: {session_id}")

                if not message:
                    self.send_response(400)
                    self._set_cors_headers()
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    response = {
                        "success": False,
                        "error": "Message is required",
                        "timestamp": datetime.now().isoformat()
                    }
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode())
                    return

                # Обрабатываем сообщение через улучшенного агента
                result = process_ai_message(message, session_id, history)

                # Формируем ответ
                response_data = {
                    "success": True,
                    "response": result.get("response", "🤖 Я понял ваш запрос."),
                    "state": result.get("state", "unknown"),
                    "quick_replies": result.get("quick_replies", []),
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat(),
                    "version": "2.0.0"
                }

                self.send_response(200)
                self._set_cors_headers()
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response_data, ensure_ascii=False, indent=2).encode())

                print(f"✅ Response sent successfully for session: {session_id}")

            except json.JSONDecodeError:
                self.send_response(400)
                self._set_cors_headers()
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    "success": False,
                    "error": "Invalid JSON format",
                    "timestamp": datetime.now().isoformat()
                }
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode())

            except Exception as e:
                print(f"❌ Error processing message: {e}")
                self.send_response(500)
                self._set_cors_headers()
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    "success": False,
                    "error": f"Internal server error: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                }
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode())

        else:
            self.send_response(404)
            self._set_cors_headers()
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"error": "Not found", "path": path}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode())

    def log_message(self, format, *args):
        """Кастомизированный лог для красивого вывода"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] 🤖 AI Agent: {format % args}")


def run_server(port=8001):
    """Запуск улучшенного AI сервера"""
    try:
        with socketserver.TCPServer(("", port), EnhancedAIHandler) as httpd:
            print(f"""
🚀 ЗАПУЩЕН УЛУЧШЕННЫЙ AI СЕРВЕР
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🤖 Сервис: Enhanced UnitySphere AI Agent
📡 Порт: {port}
🔗 URL: http://localhost:{port}
⚡ Версия: 2.0.0

✨ НОВЫЕ ВОЗМОЖНОСТИ:
• Улучшенное распознавание намерений
• Поддержка истории разговора
• Расширенные команды (помощь, сброс, поиск)
• Улучшенная валидация данных
• Более естественные ответы
• Поддержка поиска существующих клубов

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            """)

            # Запускаем сервер
            httpd.serve_forever()

    except KeyboardInterrupt:
        print("\n👋 AI сервер остановлен пользователем")
    except Exception as e:
        print(f"❌ Ошибка запуска AI сервера: {e}")
        return False

    return True


if __name__ == "__main__":
    port = 8001
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("❌ Некорректный порт, используем 8001")

    print("🚀 Запускаем улучшенный AI агент...")
    success = run_server(port)

    if not success:
        print("❌ Не удалось запустить AI сервер")
        sys.exit(1)