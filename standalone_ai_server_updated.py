#!/usr/bin/env python3
"""
🚀 Standalone AI Agent Server for Production - Updated
Lightweight server with HTML interface and AI agent - no Django dependencies
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
from datetime import datetime
import sys
import os

# Add the project directory to Python path
sys.path.insert(0, '/var/www/myapp/eventsite')

# Import our lightweight AI agent
from ai_consultant.agents.lightweight_production_agent import get_ai_response

class AIHandler(BaseHTTPRequestHandler):
    """🤖 HTTP handler for AI agent requests and HTML interface"""

    def _set_json_headers(self, status=200):
        """Set JSON response headers"""
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def _set_html_headers(self, status=200):
        """Set HTML response headers"""
        self.send_response(status)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self._set_json_headers()
        self.wfile.write(json.dumps({'status': 'ok'}).encode())

    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/api/v1/ai/production/health/' or self.path == '/health/':
            # Health check endpoint
            response = {
                'status': 'healthy',
                'service': 'UnitySphere Lightweight AI Agent',
                'version': '1.0.0',
                'timestamp': datetime.utcnow().isoformat(),
                'uptime': 'Ready'
            }
            self._set_json_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode())

        elif self.path == '/' or self.path == '/index.html':
            # Serve HTML interface
            try:
                with open('/var/www/myapp/eventsite/templates/ai_chat_interface.html', 'r', encoding='utf-8') as f:
                    html_content = f.read()
                self._set_html_headers()
                self.wfile.write(html_content.encode('utf-8'))
            except FileNotFoundError:
                # Fallback to simple HTML if file not found
                fallback_html = """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>UnitySphere AI Консультант</title>
                    <style>
                        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
                        .chat { border: 1px solid #ddd; padding: 20px; min-height: 400px; margin: 20px 0; }
                        input, button { padding: 10px; margin: 5px; font-size: 16px; }
                        .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
                        .bot { background: #f0f0f0; }
                        .user { background: #e0f0e0; text-align: right; }
                    </style>
                </head>
                <body>
                    <h1>🤖 UnitySphere AI Консультант</h1>
                    <p>Помогу создать ваш идеальный клуб через естественный диалог</p>

                    <div class="chat" id="chat">
                        <div class="message bot">👋 Привет! Я - AI консультант UnitySphere. Готов помочь создать ваш клуб!</div>
                    </div>

                    <div>
                        <input type="text" id="message" placeholder="Введите ваше сообщение..." style="width: 70%;">
                        <button onclick="sendMessage()">Отправить</button>
                    </div>

                    <script>
                        async function sendMessage() {
                            const message = document.getElementById('message').value;
                            if (!message) return;

                            // Add user message
                            const chat = document.getElementById('chat');
                            chat.innerHTML += '<div class="message user">' + message + '</div>';

                            // Clear input
                            document.getElementById('message').value = '';

                            // Send to AI
                            try {
                                const response = await fetch('/api/v1/ai/production/agent/', {
                                    method: 'POST',
                                    headers: { 'Content-Type': 'application/json' },
                                    body: JSON.stringify({
                                        message: message,
                                        session_id: 'web_demo'
                                    })
                                });

                                const data = await response.json();
                                chat.innerHTML += '<div class="message bot">' + data.response + '</div>';
                                chat.scrollTop = chat.scrollHeight;
                            } catch (error) {
                                chat.innerHTML += '<div class="message bot">Ошибка: попробуйте еще раз</div>';
                            }
                        }

                        document.getElementById('message').addEventListener('keypress', function(e) {
                            if (e.key === 'Enter') sendMessage();
                        });
                    </script>
                </body>
                </html>
                """
                self._set_html_headers()
                self.wfile.write(fallback_html.encode('utf-8'))

        else:
            self._set_html_headers(404)
            self.wfile.write(b'<h1>404 Not Found</h1>')

    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/api/v1/ai/production/agent/':
            # AI Agent endpoint
            try:
                # Get request body
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))

                # Extract message and session_id
                message = data.get('message', '').strip()
                session_id = data.get('session_id', 'default')

                if not message:
                    self._set_json_headers(400)
                    response = {
                        'success': False,
                        'error': 'Message is required',
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode())
                    return

                # Get AI response
                ai_response = get_ai_response(message, session_id)

                # Format response
                response = {
                    'success': True,
                    'response': ai_response.get('response', ''),
                    'state': ai_response.get('state', ''),
                    'timestamp': datetime.utcnow().isoformat(),
                    'session_id': session_id
                }

                # Add quick_replies if available
                if 'quick_replies' in ai_response:
                    response['quick_replies'] = ai_response['quick_replies']

                self._set_json_headers()
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode())

            except json.JSONDecodeError:
                self._set_json_headers(400)
                response = {
                    'success': False,
                    'error': 'Invalid JSON format',
                    'timestamp': datetime.utcnow().isoformat()
                }
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode())

            except Exception as e:
                self._set_json_headers(500)
                response = {
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.utcnow().isoformat()
                }
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode())

        else:
            self._set_json_headers(404)
            self.wfile.write(json.dumps({'error': 'Not found'}).encode())

    def log_message(self, format, *args):
        """Custom log format"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {self.address_string()} - {format % args}")

def run_server(host='127.0.0.1', port=8001):
    """🚀 Run the standalone AI server"""
    print(f"🚀 Starting UnitySphere AI Agent Server with HTML Interface")
    print(f"🌐 Server URL: http://{host}:{port}")
    print(f"🤖 AI Agent: http://{host}:{port}/api/v1/ai/production/agent/")
    print(f"🔍 Health Check: http://{host}:{port}/api/v1/ai/production/health/")
    print(f"🏠 Main Page: http://{host}:{port}/")
    print(f"==========================================")

    # Test AI agent before starting server
    print("🧪 Testing AI agent...")
    try:
        test_response = get_ai_response('Привет', 'test')
        if test_response and 'response' in test_response:
            print("✅ AI agent working correctly")
            print(f"Sample response: {test_response['response'][:50]}...")
        else:
            print("❌ AI agent test failed")
            return
    except Exception as e:
        print(f"❌ AI agent test failed: {e}")
        return

    # Create and start server
    server_address = (host, port)
    httpd = HTTPServer(server_address, AIHandler)

    print(f"✅ Server started successfully")
    print(f"📍 Listening on {host}:{port}")
    print(f"🔧 PID: {os.getpid()}")
    print("")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        httpd.server_close()
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        httpd.server_close()

if __name__ == '__main__':
    # Ensure we're in the right directory
    os.chdir('/var/www/myapp/eventsite')

    # Activate virtual environment
    activate_script = '/var/www/myapp/eventsite/venv/bin/activate_this.py'
    if os.path.exists(activate_script):
        exec(open(activate_script).read())

    run_server()