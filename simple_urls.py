"""
Simple URL patterns for basic functionality
"""
from django.urls import path
from django.http import HttpResponse
import os

def simple_ai_page(request):
    """Простая страница AI консультанта"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Консультант - UnitySphere</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
            <div class="container">
                <a class="navbar-brand" href="/">🎯 UnitySphere</a>
                <div class="navbar-nav ms-auto">
                    <a class="nav-item nav-link" href="/">Главная</a>
                    <a class="nav-item nav-link" href="/admin/">Админ</a>
                </div>
            </div>
        </nav>

        <div class="container mt-4">
            <div class="row">
                <div class="col-md-12">
                    <h1>🤖 AI Консультант</h1>
                    <p class="lead">Помощь в создании и развитии фан-клубов</p>

                    <div class="alert alert-info">
                        <h5>ℹ️ Сайт работает в упрощенном режиме</h5>
                        <p>Все основные функции доступны:</p>
                        <ul>
                            <li>✅ Регистрация и авторизация</li>
                            <li>✅ Создание фан-клубов</li>
                            <li>✅ Поиск и присоединение к клубам</li>
                            <li>✅ Администрирование</li>
                        </ul>
                    </div>

                    <div class="card">
                        <div class="card-body">
                            <h5>🎯 Как создать успешный фан-клуб:</h5>
                            <ol>
                                <li><strong>Определите направление:</strong> Выберите тему, которая вас увлекает</li>
                                <li><strong>Придумайте название:</strong> Оно должно быть запоминающимся и отражать суть клуба</li>
                                <li><strong>Создайте описание:</strong> Расскажите, чем будет заниматься ваш клуб</li>
                                <li><strong>Привлекайте участников:</strong> Расскажите друзьям, разместите информацию в соцсетях</li>
                                <li><strong>Организуйте первые мероприятия:</strong> Начните с небольших встреч</li>
                            </ol>

                            <div class="mt-3">
                                <a href="/" class="btn btn-primary">На главную</a>
                                <a href="/admin/" class="btn btn-secondary">Админка</a>
                            </div>
                        </div>
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
    path('ai/consultant/', simple_ai_page, name='ai_consultant'),
]