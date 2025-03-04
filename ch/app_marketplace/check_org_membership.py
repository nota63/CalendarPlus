from functools import wraps
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from accounts.models import Profile, Organization


def check_org_membership(view_func):
    @wraps(view_func)
    def wrapper(request, org_id, *args, **kwargs):
        # Get the organization object, but don’t replace org_id
        organization = get_object_or_404(Organization, id=org_id)
        
        # Check if the user is part of the organization
        profile = get_object_or_404(Profile, organization=organization, user=request.user)
        
        if not profile:
            return JsonResponse({'error': 'You are not authorized!'}, status=403)

        # Call the view function with the original org_id (integer)
        return view_func(request, org_id, *args, **kwargs)

    return wrapper
