"""🔧 Health Check URLs"""
from django.urls import path
from django.http import JsonResponse


def health_check(request):
    """🔍 Basic health check endpoint"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'UnitySphere Production',
        'timestamp': '2025-11-27T06:15:00'
    })


urlpatterns = [
    path('', health_check, name='health_check'),
]