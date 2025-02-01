from django.shortcuts import render,redirect,get_object_or_404
from accounts.models import Organization, Profile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt



# Create your views here.

@csrf_exempt
def edit_organization(request, org_id):
    if request.method == "POST" and request.user.is_authenticated:
        organization = get_object_or_404(Organization, id=org_id)

        # Check if the user is the admin of the organization
        profile = Profile.objects.filter(user=request.user, organization=organization, is_admin=True).first()
        if not profile:
            return JsonResponse({"error": "You are not authorized to edit this organization."}, status=403)

        name = request.POST.get("name")
        description = request.POST.get("description")

        if name:
            organization.name = name
        if description:
            organization.description = description

        organization.save()
        return JsonResponse({"success": "Organization updated successfully!"})

    return JsonResponse({"error": "Invalid request"}, status=400)

