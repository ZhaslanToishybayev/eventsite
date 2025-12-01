"""🎯 Temporary Production URLs - Lightweight AI Only"""

from django.urls import path
from django.http import JsonResponse
from ai_consultant.agents.lightweight_production_agent import get_ai_response
import json

def health_check(request):
    """🔍 Health check endpoint"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'UnitySphere Lightweight AI Agent',
        'version': '1.0.0',
        'timestamp': '2025-11-27T06:15:00'
    })

def production_ai_agent(request):
    """🤖 Production AI Agent endpoint"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '')
            session_id = data.get('session_id', 'default')

            response = get_ai_response(message, session_id)

            return JsonResponse({
                'success': True,
                'response': response.get('response', ''),
                'state': response.get('state', ''),
                'timestamp': '2025-11-27T06:15:00',
                'session_id': session_id
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e),
                'timestamp': '2025-11-27T06:15:00'
            }, status=500)
    else:
        return JsonResponse({'error': 'POST method required'}, status=405)

urlpatterns = [
    path('api/v1/ai/production/health/', health_check, name='health_check'),
    path('api/v1/ai/production/agent/', production_ai_agent, name='production_ai_agent'),
    path('health/', health_check, name='main_health'),
]
