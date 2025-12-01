
from django.contrib import admin
from django.urls import path
from django.http import JsonResponse, HttpResponse
import json

def api_root(request):
    return JsonResponse({
        'name': 'UnitySphere Lightweight API',
        'version': 'v1',
        'status': 'active',
        'message': 'System is running with lightweight configuration',
        'endpoints': {
            'health': '/health/',
            'test': '/test/'
        }
    })

def health_check(request):
    return JsonResponse({
        'status': 'healthy',
        'service': 'Lightweight Django',
        'timestamp': '2024-11-26T23:30:00Z'
    })

def test_endpoint(request):
    # Тестируем облегченный агент
    try:
        from ai_consultant.agents.lightweight_agent import get_lightweight_agent

        agent = get_lightweight_agent()
        result = agent.process_message("Test message", "test_user")

        return JsonResponse({
            'status': 'success',
            'agent_test': 'passed',
            'response': result['response'][:50] + '...',
            'progress': f"{result['progress']['progress_percentage']}%",
            'intent': result['analysis']['intent']
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'agent_test': 'failed',
            'error': str(e)
        }, status=500)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/ai/health/', health_check, name='health'),
    path('api/v1/ai/test/', test_endpoint, name='test'),
    path('', api_root),
]
