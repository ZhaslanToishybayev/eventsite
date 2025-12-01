from django.http import HttpResponse
from django.template import Template, Context

def simple_index(request):
    html = """
    <html>
    <head><title>Test Index</title></head>
    <body>
        <h1>ТЕСТ: Index view работает!</h1>
        <p>Если вы видите этот текст, значит view вызывается.</p>
        <div class="banner-area">BANNER AREA TEST</div>
    </body>
    </html>
    """
    return HttpResponse(html)