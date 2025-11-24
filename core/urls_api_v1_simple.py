"""
Simple API v1 URLs - без проблемных зависимостей
"""
from django.urls import path, include
from django.http import JsonResponse

def api_root(request):
    """API root endpoint"""
    return JsonResponse({
        'name': 'UnitySphere API',
        'version': 'v1',
        'status': 'working',
        'endpoints': {
            'status': '/api/v1/status/',
            'ai': '/api/v1/ai/ (временно отключен)'
        }
    })

urlpatterns = [
    path('', api_root, name='api_root'),
    path('status/', include('simple_api_urls')),
    # Временно отключаем AI маршруты
    # path('ai/', include('simple_urls')),
]