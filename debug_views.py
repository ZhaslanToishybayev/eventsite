from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone

def debug_widget_view(request):
    """
    Отладочная страница для AI виджета
    """
    return render(request, 'debug_widget.html')

@csrf_exempt
@require_http_methods(["GET", "POST"])
def debug_widget_test(request):
    """
    Тестовый эндпоинт для проверки виджета
    """
    if request.method == 'POST':
        # Эмуляция ответа API
        response_data = {
            'response': 'Привет! Я AI-консультант платформы ЦЕНТР СОБЫТИЙ. Я могу помочь вам найти интересные клубы и сообщества. Чем могу помочь?',
            'session_id': 'test-session-123',
            'success': True
        }
        return JsonResponse(response_data)

    # GET запрос - информация о состоянии
    return JsonResponse({
        'status': 'ok',
        'message': 'Debug endpoint is working',
        'timestamp': timezone.now().isoformat()
    })