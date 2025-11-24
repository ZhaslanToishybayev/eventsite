"""
Simple URLs for UnitySphere - без проблемных зависимостей
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
import os

def home(request):
    """Главная страница"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>UnitySphere - fan-club.kz</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            .hero {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 100px 0;
                text-align: center;
            }
            .feature-box {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                margin-bottom: 30px;
            }
        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
            <div class="container">
                <a class="navbar-brand" href="/">🎯 UnitySphere</a>
                <div class="navbar-nav ms-auto">
                    <a class="nav-item nav-link" href="/">Главная</a>
                    <a class="nav-item nav-link" href="/admin/">Админ</a>
                    <a class="nav-item nav-link" href="/ai/consultant/">AI Консультант</a>
                </div>
            </div>
        </nav>

        <div class="hero">
            <div class="container">
                <h1>🎯 UnitySphere - fan-club.kz</h1>
                <p class="lead">Платформа для создания и управления фан-клубами</p>
                <a href="/admin/" class="btn btn-light btn-lg">Начать</a>
            </div>
        </div>

        <div class="container mt-5">
            <div class="row">
                <div class="col-md-4">
                    <div class="feature-box">
                        <h3>👥 Создавайте клубы</h3>
                        <p>Создавайте фан-клубы по любым интересам и темам. Объединяйте единомышленников.</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="feature-box">
                        <h3>🔍 Находите клубы</h3>
                        <p>Ищите и присоединяйтесь к существующим клубам по своим интересам.</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="feature-box">
                        <h3>🎉 Организовывайте события</h3>
                        <p>Планируйте и проводите мероприятия, встречи и конкурсы.</p>
                    </div>
                </div>
            </div>

            <div class="row mt-5">
                <div class="col-12">
                    <div class="alert alert-info">
                        <h4>🚀 Сайт работает!</h4>
                        <p>Все основные функции доступны. Для управления сайтом перейдите в <a href="/admin/">админ-панель</a>.</p>
                        <p><strong>AI Консультант:</strong> <a href="/ai/consultant/">Помощь в создании клубов</a></p>
                    </div>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """
    return HttpResponse(html)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('core.urls_api_v1_simple')),
    path('ai/consultant/', include('simple_urls')),
    path('', home, name='home'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)