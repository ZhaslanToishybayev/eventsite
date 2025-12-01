#!/usr/bin/env python3
"""
🚀 Conversational AI Agent Server for UnitySphere
Новый сервер с улучшенным conversational AI агентом
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
    from conversational_production_agent import ConversationalAIConsultant, process_conversational_message
    print("✅ Загружен ConversationalAIConsultant")
except ImportError as e:
    print(f"❌ Ошибка импорта ConversationalAIConsultant: {e}")
    sys.exit(1)

class ConversationalAIHandler(http.server.BaseHTTPRequestHandler):
    """🤖 Обработчик запросов для conversational AI агента"""

    def __init__(self, *args, **kwargs):
        self.ai_agent = ConversationalAIConsultant()
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
                "service": "Conversational UnitySphere AI Agent",
                "version": "3.0.0",
                "features": [
                    "Natural conversational flow",
                    "Club creation workflow",
                    "Broad context understanding",
                    "Lightweight responses",
                    "Emotional intelligence"
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
                "ai_agent": "ConversationalAIConsultant",
                "timestamp": datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode())

        elif path == '/info':
            self.send_response(200)
            self._set_cors_headers()
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            response = {
                "service": "Conversational UnitySphere AI Agent",
                "version": "3.0.0",
                "description": "Advanced conversational AI for club creation",
                "features": {
                    "natural_language": "Natural, friendly conversation flow",
                    "broad_context": "Understands wide context and intentions",
                    "lightweight": "Fast, non-repetitive responses",
                    "emotional": "Friendly, supportive communication style",
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

                # Обрабатываем сообщение через conversational агента
                result = process_conversational_message(message, session_id, history)

                # Формируем ответ
                response_data = {
                    "success": True,
                    "response": result.get("response", "🤖 Понял тебя!"),
                    "state": result.get("state", "unknown"),
                    "quick_replies": result.get("quick_replies", []),
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat(),
                    "version": "3.0.0"
                }

                # Добавляем action если есть
                if result.get("action"):
                    response_data["action"] = result.get("action")

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
        print(f"[{timestamp}] 🤖 Conversational AI: {format % args}")


def run_server(port=8002):
    """Запуск conversational AI сервера"""
    try:
        with socketserver.TCPServer(("", port), ConversationalAIHandler) as httpd:
            print(f"""
🚀 ЗАПУЩЕН CONVERSATIONAL AI СЕРВЕР
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🤖 Сервис: Conversational UnitySphere AI Agent
📡 Порт: {port}
🔗 URL: http://localhost:{port}
⚡ Версия: 3.0.0

✨ НОВЫЕ ВОЗМОЖНОСТИ:
• Естественное, легкое общение
• Широкий контекст понимания
• Неповторяющиеся, живые ответы
• Дружелюбный, поддерживающий стиль
• Улучшенное распознавание намерений
• Более гибкие команды

🎯 ДОСТУПНЫЕ КОМАНДЫ:
• помощь/help - Справка по использованию
• сброс/reset - Начать диалог сначала
• пока/goodbye - Завершить диалог
• найти клубы - Поиск существующих клубов

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            """)

            # Запускаем сервер
            httpd.serve_forever()

    except KeyboardInterrupt:
        print("\n👋 Conversational AI сервер остановлен пользователем")
    except Exception as e:
        print(f"❌ Ошибка запуска AI сервера: {e}")
        return False

    return True


if __name__ == "__main__":
    port = 8002
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("❌ Некорректный порт, используем 8002")

    print("🚀 Запускаем conversational AI агента...")
    success = run_server(port)

    if not success:
        print("❌ Не удалось запустить conversational AI сервер")
        sys.exit(1)