from django.shortcuts import redirect
from django.urls import reverse
from organizations.models import OrganizationProtection
from django.contrib.auth import get_user



# class OrganizationPasswordMiddleware:
#     """Middleware to enforce organization password entry every time."""

#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         user = get_user(request)  # ✅ Ensure we get the user object safely

#         if user.is_authenticated and request.path.startswith("/calendar/org_detail/"):
#             try:
#                 org_id = request.path.split("/")[-2]  # Extract org_id from URL
#                 org_protection = OrganizationProtection.objects.get(organization_id=org_id)

#                 if org_protection.protection_status:
#                     if not request.session.get(f"org_temp_access_{org_id}"):
#                         return redirect('validate_org_passwords', org_id=org_id)
#                     else:
#                         # 🧹 Remove session key after allowing first access
#                         del request.session[f"org_temp_access_{org_id}"]

#             except OrganizationProtection.DoesNotExist:
#                 pass  

#         return self.get_response(request)




# NEW MIDDLEWARE PROTECTION
class OrganizationPasswordMiddleware:
    """Middleware to enforce organization password entry based on enabled protections."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = get_user(request)  # ✅ Ensure we get the user object safely

        if user.is_authenticated:
            try:
                org_id = None
                protection_field = None

                # 🔍 Detect and extract org_id based on the URL pattern
                if request.path.startswith("/calendar/org_detail/"):
                    org_id = request.path.split("/")[-2]  # Extract org_id
                    protection_field = "protect_org_detail"

                elif request.path.startswith("/channels/organization/"):
                    parts = request.path.split("/")
                    if len(parts) > 4 and parts[2] == "organization":
                        org_id = parts[3]  # ✅ org_id is at index 3
                        protection_field = "protect_channels"

                elif request.path.startswith("/groups/groups/user/"):
                    parts = request.path.split("/")
                    if len(parts) > 4 and parts[3] == "user":
                        org_id = parts[4]  # ✅ org_id is at index 4
                        protection_field = "protect_groups"

                if org_id and protection_field:
                    org_protection = OrganizationProtection.objects.get(organization_id=int(org_id))  # Ensure it's an integer

                    # ✅ Check if protection is enabled for the specific section
                    if getattr(org_protection, protection_field, False):
                        if not request.session.get(f"org_temp_access_{org_id}"):
                            return redirect('validate_org_passwords', org_id=org_id)
                        else:
                            # 🧹 Remove session key after allowing first access
                            del request.session[f"org_temp_access_{org_id}"]

            except (OrganizationProtection.DoesNotExist, ValueError):
                pass  # Avoid crashing if org_id is invalid

        return self.get_response(request)