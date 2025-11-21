from django.shortcuts import redirect
from django.urls import reverse

class RequirePhoneMiddleware:
    """
    Middleware that checks if the authenticated user has a valid phone number.
    If the user has a dummy phone number (starting with +7000), they are redirected
    to the phone setting page.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Check if user has a dummy phone number
            # We assume dummy numbers start with +7000 (as set in the adapter)
            if request.user.phone and request.user.phone.startswith('+7000'):
                # Allow access to these paths without phone verification
                allowed_paths = [
                    reverse('set_phone'),
                    reverse('account_logout'),
                    '/accounts/logout/',
                    '/admin/',
                    '/static/',  # Allow static files
                    '/media/',   # Allow media files
                    '/api/',     # Allow API calls
                ]
                
                # Check if current path is allowed
                if not any(request.path.startswith(path) for path in allowed_paths):
                    return redirect('set_phone')

        response = self.get_response(request)
        return response
