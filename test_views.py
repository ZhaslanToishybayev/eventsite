from django.shortcuts import render

def test_interactive_ai_view(request):
    """Тестовая страница для интерактивного AI"""
    return render(request, 'test_interactive_ai.html')