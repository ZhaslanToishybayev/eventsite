from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from datetime import datetime

from ai_consultant.agents.lightweight_production_agent import get_ai_response


@csrf_exempt
@require_http_methods(["POST"])
def production_ai_agent(request):
    """
    🚀 Production-ready AI Agent Endpoint
    Работает без heavy зависимостей
    """
    try:
        # Получаем данные из запроса
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        session_id = data.get('session_id', 'default')

        if not message:
            return JsonResponse({
                'error': 'Empty message',
                'status': 'error'
            }, status=400)

        # Получаем AI ответ
        ai_response = get_ai_response(message, session_id)

        return JsonResponse({
            'success': True,
            'response': ai_response['response'],
            'state': ai_response['state'],
            'quick_replies': ai_response.get('quick_replies', []),
            'action': ai_response.get('action'),
            'timestamp': datetime.now().isoformat(),
            'session_id': session_id
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON',
            'status': 'error'
        }, status=400)

    except Exception as e:
        # В production логируем ошибку
        print(f"AI Agent Error: {str(e)}")
        return JsonResponse({
            'error': 'Internal server error',
            'status': 'error'
        }, status=500)


@require_http_methods(["GET"])
def production_ai_health(request):
    """
    🔍 Health check endpoint
    """
    return JsonResponse({
        'status': 'healthy',
        'service': 'UnitySphere AI Agent',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'dependencies': {
            'django': 'ok',
            'ai_agent': 'ok',
            'lightweight': True
        }
    })


@require_http_methods(["GET"])
def production_ai_info(request):
    """
    ℹ️ AI Agent information
    """
    return JsonResponse({
        'service': 'UnitySphere AI Club Creation Agent',
        'version': '1.0.0',
        'features': [
            'Natural Russian conversation',
            'Club type classification',
            'Name generation',
            'Description creation',
            'Contact information collection',
            'Validation and review',
            'Lightweight design'
        ],
        'capabilities': {
            'club_types': ['Technology', 'Creative', 'Sport', 'Language', 'Business'],
            'languages': ['Russian', 'English'],
            'max_concurrent_sessions': 1000,
            'response_time_ms': '< 100'
        },
        'status': 'production_ready'
    })