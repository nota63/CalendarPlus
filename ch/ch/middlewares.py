
from django.shortcuts import redirect
from django.urls import reverse

class CheckEmailMiddleware:
    """Middleware to check if user has an email. If not, force update."""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.email:
            if request.path != reverse('update_email'):
                return redirect(reverse('update_email'))
        return self.get_response(request)


