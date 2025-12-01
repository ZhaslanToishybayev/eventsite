"""📋 Django API для проксирования AI агента"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import requests
import json
from datetime import datetime

@csrf_exempt
@require_http_methods(["POST"])
def proxy_ai_agent(request):
    """
    🚀 Прокси для AI агента
    Перенаправляет запросы от Django к AI агенту на порту 8001
    """
    try:
        # Получаем данные из запроса
        request_body = request.body
        if isinstance(request_body, bytes):
            request_body = request_body.decode('utf-8')

        data = json.loads(request_body)
        message = data.get('message', '').strip()
        session_id = data.get('session_id', 'default')

        if not message:
            return JsonResponse({
                'success': False,
                'error': 'Empty message',
                'status': 'error'
            }, status=400)

        # Проксируем запрос к AI агенту
        ai_agent_url = 'http://127.0.0.1:8001/api/agent'

        ai_response = requests.post(ai_agent_url, json={
            'message': message,
            'session_id': session_id
        }, timeout=30)

        if ai_response.status_code == 200:
            ai_data = ai_response.json()
            return JsonResponse({
                'success': True,
                'response': ai_data.get('response', ''),
                'state': ai_data.get('state', ''),
                'quick_replies': ai_data.get('quick_replies', []),
                'action': ai_data.get('action'),
                'timestamp': datetime.now().isoformat(),
                'session_id': session_id
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'AI agent error',
                'status': 'error'
            }, status=ai_response.status_code)

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON',
            'status': 'error'
        }, status=400)

    except requests.RequestException as e:
        return JsonResponse({
            'success': False,
            'error': f'Connection error: {str(e)}',
            'status': 'error'
        }, status=500)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Internal error: {str(e)}',
            'status': 'error'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def proxy_conversational_ai_agent(request):
    """
    🚀 Прокси для Conversational AI агента
    Перенаправляет запросы от Django к Conversational AI агенту на порту 8002
    """
    try:
        # Получаем данные из запроса
        request_body = request.body
        if isinstance(request_body, bytes):
            request_body = request_body.decode('utf-8')

        data = json.loads(request_body)
        message = data.get('message', '').strip()
        session_id = data.get('session_id', 'default')

        if not message:
            return JsonResponse({
                'success': False,
                'error': 'Empty message',
                'status': 'error'
            }, status=400)

        # Проксируем запрос к Conversational AI агенту
        ai_agent_url = 'http://127.0.0.1:8002/api/agent'

        ai_response = requests.post(ai_agent_url, json={
            'message': message,
            'session_id': session_id
        }, timeout=30)

        if ai_response.status_code == 200:
            ai_data = ai_response.json()
            return JsonResponse({
                'success': True,
                'response': ai_data.get('response', ''),
                'state': ai_data.get('state', ''),
                'quick_replies': ai_data.get('quick_replies', []),
                'session_id': session_id,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Conversational AI agent error',
                'status': 'error'
            }, status=ai_response.status_code)

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON',
            'status': 'error'
        }, status=400)

    except requests.RequestException as e:
        return JsonResponse({
            'success': False,
            'error': f'Connection error: {str(e)}',
            'status': 'error'
        }, status=500)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Internal error: {str(e)}',
            'status': 'error'
        }, status=500)


@require_http_methods(["GET"])
def proxy_ai_health(request):
    """
    🔍 Health check для AI агента через прокси
    """
    try:
        ai_health_url = 'http://127.0.0.1:8001/api/v1/ai/production/health/'
        ai_response = requests.get(ai_health_url, timeout=10)

        if ai_response.status_code == 200:
            ai_data = ai_response.json()
            return JsonResponse({
                'status': 'healthy',
                'service': 'UnitySphere Django Proxy + AI Agent',
                'version': '1.0.0',
                'timestamp': datetime.now().isoformat(),
                'ai_agent_status': ai_data
            })
        else:
            return JsonResponse({
                'status': 'unhealthy',
                'service': 'UnitySphere Django Proxy',
                'error': 'AI agent not responding',
                'timestamp': datetime.now().isoformat()
            }, status=503)

    except requests.RequestException:
        return JsonResponse({
            'status': 'unhealthy',
            'service': 'UnitySphere Django Proxy',
            'error': 'AI agent connection failed',
            'timestamp': datetime.now().isoformat()
        }, status=503)


@require_http_methods(["GET"])
def proxy_ai_info(request):
    """
    ℹ️ Информация о AI агенте через прокси
    """
    try:
        ai_info_url = 'http://127.0.0.1:8001/api/v1/ai/production/info/'
        ai_response = requests.get(ai_info_url, timeout=10)

        if ai_response.status_code == 200:
            ai_data = ai_response.json()
            return JsonResponse({
                'service': 'UnitySphere Django Proxy Service',
                'version': '1.0.0',
                'ai_agent_info': ai_data,
                'proxy_status': 'active',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return JsonResponse({
                'service': 'UnitySphere Django Proxy',
                'error': 'AI agent info unavailable',
                'timestamp': datetime.now().isoformat()
            }, status=503)

    except requests.RequestException as e:
        return JsonResponse({
            'service': 'UnitySphere Django Proxy',
            'error': f'Connection failed: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }, status=503)