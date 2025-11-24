"""
Simple API URLs without problematic dependencies
"""
from django.urls import path
from django.http import JsonResponse

def api_status(request):
    """API status endpoint"""
    return JsonResponse({
        'status': 'working',
        'message': 'UnitySphere API работает',
        'features': [
            'Пользовательская система',
            'Создание клубов',
            'Поиск клубов',
            'Администрирование'
        ]
    })

urlpatterns = [
    path('status/', api_status, name='api_status'),
]