
from django.shortcuts import redirect
from django.urls import reverse


class CheckEmailMiddleware:
    """Middleware to check if a logged-in user has an email. If not, force update."""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated: 
            if not request.user.email and request.path not in [reverse('update_email'), reverse('logout')]:
                return redirect(reverse('update_email'))
                
        return self.get_response(request)



# FIRST TIME GUIDE MIDDLEWARE

from django.shortcuts import redirect

class FirstTimeGuideMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == "/calendar/organizations/" and not request.session.get("seen_guide"):
            return redirect("guide_page")  

        return self.get_response(request)



# guide when user first time visit to org_detail page
class OrgGuideMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/calendar/org_detail/") and not request.session.get("seen_guide"):
            # Extract org_id from the URL
            org_id = request.path.split("/")[-2]  
            request.session["org_id"] = org_id 

            return redirect(reverse("org_guide"))  

        return self.get_response(request)