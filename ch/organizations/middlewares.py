from django.shortcuts import redirect
from django.urls import reverse
from organizations.models import OrganizationProtection
from django.contrib.auth import get_user


class OrganizationPasswordMiddleware:
    """Middleware to check if an organization requires a password before access."""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = get_user(request)  # ✅ Ensure we get the user object safely

        if user.is_authenticated and request.path.startswith("/calendar/org_detail/"):
            try:
                org_id = request.path.split("/")[-2]  # Extract org_id from URL
                org_protection = OrganizationProtection.objects.get(organization_id=org_id)

                if org_protection.protection_status and not request.session.get(f"org_access_{org_id}"):
                    # return redirect(reverse("validate_org_passwords",kwargs={"org_id": org_id}))
                    return redirect('validate_org_passwords',org_id=org_id)
                
            except OrganizationProtection.DoesNotExist:
                pass  # Organization has no password, continue as normal

        return self.get_response(request)