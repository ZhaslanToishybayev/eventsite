import re
from django.http import HttpResponsePermanentRedirect

class HTTPToHTTPSRedirectMiddleware:
    """
    Middleware для перенаправления всего HTTP трафика на HTTPS
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Если запрос пришел по HTTP
        if not request.is_secure():
            # Получаем имя хоста из запроса
            host = request.get_host().split(':')[0]
            # Формируем HTTPS URL
            url = f"https://{host}:8443{request.get_full_path()}"
            # Перенаправляем на HTTPS
            return HttpResponsePermanentRedirect(url)

        return self.get_response(request)