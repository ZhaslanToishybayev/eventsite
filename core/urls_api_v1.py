"""
Complete API v1 URLs - Все AI функции доступны
"""
from django.urls import path, include
from django.http import JsonResponse

def api_root(request):
    """API root endpoint"""
    return JsonResponse({
        'name': 'UnitySphere API',
        'version': 'v1',
        'status': 'working',
        'features': ['AI Chat', 'Club Creation', 'Development', 'Feedback', 'Interview Studio'],
        'endpoints': {
            'ai_chat': '/api/v1/ai/chat/',
            'ai_simple': '/api/v1/ai/simple-chat/',
            'ai_health': '/api/v1/ai/health/',
            'club_creation': '/api/v1/ai/chat/club-creation/ideas/',
            'development': '/api/v1/ai/chat/development/paths/',
            'feedback': '/api/v1/ai/chat/feedback/',
            'interview': '/api/v1/ai/chat/interview/'
        }
    })

urlpatterns = [
    path('', api_root, name='api_root'),
    path('ai/', include('core.urls_ai_complete')),
    path('status/', include('core.simple_api_urls_new')),

    # 🚀 Enhanced AI API with RAG and Recommendations
    path('ai/enhanced/', include('ai_consultant.api.enhanced_urls')),

    # 🤖 Club Creation Agent API
    path('ai/club-creation/', include('ai_consultant.api.club_creation_urls')),

    # 📚 Clubs API - CRUD operations for clubs
    path('clubs/', include('clubs.api.urls')),
]
