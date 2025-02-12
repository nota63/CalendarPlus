from accounts.models import Profile

def user_profile(request):
    if request.user.is_authenticated:
        user_profiles = Profile.objects.filter(user=request.user).select_related("organization")

        profile = user_profiles.first()  # Get the first matching profile if available
        organization = profile.organization if profile and profile.organization else None  # Ensure org_id is always available

        return {
            "profile": profile,
            "organization": organization,  # Make org_id accessible in templates
            "is_admin": user_profiles.filter(is_admin=True).exists(),
            "is_manager": user_profiles.filter(is_manager=True).exists(),
            "is_employee": user_profiles.filter(is_employee=True).exists(),
        }
    return {"profile": None, "org_id": None, "is_admin": False, "is_manager": False, "is_employee": False}
