from django.shortcuts import render
from django.http import HttpResponse

def test_view(request):
    return HttpResponse("""
    <html>
    <head><title>Test Page</title></head>
    <body>
        <h1>ТЕСТ: Django работает!</h1>
        <p>Если вы видите этот текст, значит view работает.</p>
    </body>
    </html>
    """)