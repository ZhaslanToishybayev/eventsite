from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.conf import settings
from django import views as django_views
from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView

def test_chat_view(request):
    """Страница для тестирования ИИ-консультанта"""
    return render(request, 'test_chat.html')

def serena_demo_view(request):
    """Страница для демонстрации Serena AI"""
    return render(request, 'serena_demo.html')

def ai_chat_demo_v2_view(request):
    """Страница для демонстрации ИИ-консультанта v2.0"""
    return render(request, 'ai-chat-demo-v2.html')

def debug_widget_view(request):
    """Тестовая страница для отладки AI виджета"""
    return render(request, 'debug_widget.html')

def test_widget_minimal_view(request):
    """Минимальная тестовая страница для AI виджета"""
    return render(request, 'test-widget-minimal.html')

def debug_main_page_view(request):
    """Диагностика главной страницы для AI виджета"""
    return render(request, 'debug-main-page.html')

def test_simple_view(request):
    """Простой тест виджета"""
    return render(request, 'test-simple.html')

def ai_demo_view(request):
    """Демонстрационная страница AI консультанта"""
    return render(request, 'ai_demo.html')

urlpatterns = [
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('admin/', admin.site.urls),
    path('api/v1/', include('core.urls_api_v1')),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('allauth.urls')),
    path('test-chat/', test_chat_view, name='test_chat'),
    path('serena-demo/', serena_demo_view, name='serena_demo'),
    path('ai-chat-demo-v2/', ai_chat_demo_v2_view, name='ai_chat_demo_v2'),
    path('debug-widget/', debug_widget_view, name='debug_widget'),
    path('test-widget-minimal/', test_widget_minimal_view, name='test_widget_minimal'),
    path('debug-main-page/', debug_main_page_view, name='debug_main_page'),
    path('test-simple/', test_simple_view, name='test_simple'),
    path('ai-demo/', ai_demo_view, name='ai_demo'),
    path('', include('clubs.urls')),
    re_path(r'^jsi18n/$', django_views.i18n.JavaScriptCatalog.as_view(), name='jsi18n'),
]


def custom_403(request, exception):
    return render(request, 'errors/403.html', status=403)


handler403 = custom_403


# if settings.DEBUG:
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
