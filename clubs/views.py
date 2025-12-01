from django.shortcuts import render
from django.http import HttpResponse
import json
from datetime import datetime
from django.utils import timezone

def index_view(request):
    """HTML view for main page"""
    print(f"DEBUG: index_view called with path: {request.path}, method: {request.method}")
    print(f"DEBUG: Accept header: {request.headers.get('Accept')}")
    print(f"DEBUG: GET params: {dict(request.GET)}")

    if request.path == '/' and request.method == 'GET':
        # Check if this is an API request (has specific Accept header or format parameter)
        accept_header = request.headers.get('Accept', '')
        format_param = request.GET.get('format', '')

        is_api_request = (
            'application/json' in accept_header or
            format_param == 'json' or
            'api' in request.path.lower()
        )

        # Force HTML mode if explicitly requested
        force_html = format_param == 'html'

        print(f"DEBUG: accept_header: '{accept_header}'")
        print(f"DEBUG: format_param: '{format_param}'")
        print(f"DEBUG: is_api_request: {is_api_request}, force_html: {force_html}")

        if force_html:
            is_api_request = False

        print(f"DEBUG: is_api_request: {is_api_request}")

        if is_api_request:
            print("DEBUG: Returning JSON response")
            return HttpResponse(
                json.dumps({
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
                    "website": "https://fan-club.kz",
                    "ai_widget": "Available with 5 features",
                    "ssl": "Let's Encrypt enabled"
                }),
                content_type="application/json"
            )
        else:
            print("DEBUG: Returning HTML response")
            html_content = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fan Club - Главная</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; color: white; }
        .container { background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); border-radius: 20px; padding: 40px; text-align: center; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1); }
        h1 { font-size: 3em; margin-bottom: 20px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        .status { background: rgba(0, 255, 0, 0.2); border: 2px solid rgba(0, 255, 0, 0.5); border-radius: 10px; padding: 20px; margin: 20px 0; }
        .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0; }
        .feature { background: rgba(255, 255, 255, 0.1); padding: 20px; border-radius: 10px; border-left: 4px solid #fff; }
        .ai-widget-status { background: rgba(0, 255, 255, 0.2); border: 2px solid rgba(0, 255, 255, 0.5); margin: 20px 0; padding: 20px; border-radius: 10px; }
        .ssl-badge { background: rgba(255, 215, 0, 0.2); border: 2px solid rgba(255, 215, 0, 0.5); color: #fff; padding: 10px; border-radius: 5px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 Fan Club</h1>
        <p>Платформа для фан-клубов и мероприятий</p>

        <div class="status">
            <h2>✅ Сайт работает нормально</h2>
            <p>SSL: Let's Encrypt | Django: 4.2+ | Python: 3.12+</p>
        </div>

        <div class="ssl-badge">
            🔒 SSL сертификат: Let's Encrypt (авто-обновление)
        </div>

        <div class="ai-widget-status">
            <h3>🤖 AI Консультант</h3>
            <p><strong>5 функций активировано:</strong></p>
            <ul style="text-align: left; display: inline-block;">
                <li>🎬 Анимации появления</li>
                <li>🔊 Звуковые эффекты</li>
                <li>💡 Умные подсказки</li>
                <li>🌙 Темная тема</li>
                <li>🔔 Уведомления</li>
            </ul>
        </div>

        <div class="features">
            <div class="feature">
                <h4>📱 Виджет</h4>
                <p>Интерактивный AI консультант в правом нижнем углу</p>
            </div>
            <div class="feature">
                <h4>🔒 Безопасность</h4>
                <p>HTTPS с Let's Encrypt сертификатами</p>
            </div>
            <div class="feature">
                <h4>⚡ Производительность</h4>
                <p>nginx + Django + оптимизация</p>
            </div>
        </div>

        <div style="margin-top: 30px;">
            <p><em>Откройте сайт в браузере чтобы увидеть полную версию с AI виджетом</em></p>
            <p><strong>Сайт:</strong> https://fan-club.kz</p>
        </div>
    </div>
</body>
</html>"""
            return HttpResponse(html_content, content_type="text/html")
    return HttpResponse("Not found", status=404)

def health_view(request):
    """Health check endpoint"""
    return HttpResponse(
        json.dumps({
            "status": "healthy",
            "service": "Enhanced UnitySphere AI Agent",
            "version": "2.0.0",
            "timestamp": str(timezone.now())
        }),
        content_type="application/json"
    )
