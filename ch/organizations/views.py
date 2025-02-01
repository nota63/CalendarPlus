from django.shortcuts import render,redirect,get_object_or_404
from accounts.models import(Organization, Profile, EmailInvitation)
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


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



# Organization Invitations

@login_required
def organization_invitations(request, org_id):
 
    organization = get_object_or_404(Organization, id=org_id)
    
 
    profile = organization.profiles.filter(user=request.user).first()
    if not profile or not profile.is_admin:
        raise PermissionDenied("You do not have permission to view this organization's invitations.")
    
   
    invitations = EmailInvitation.objects.filter(organization=organization)


  
    invitation_data = []
    for invitation in invitations:
        invitation_data.append({
            'inviter':invitation.inviter.username,
            'invitee_email': invitation.invitee_email,
            'role': invitation.get_role_display(),
            'status': invitation.get_status_display(),
            'expires_at': invitation.expires_at.strftime('%Y-%m-%d %H:%M'),
        })
    
    return JsonResponse({'invitations': invitation_data})


# CUSTOMIZE ORGANIZATION AND MANAGE

@login_required
def customize_workspace(request, org_id):
    organization = get_object_or_404(Organization, id=org_id)
    profile = organization.profiles.filter(user=request.user).first()
    if not profile or not profile.is_admin:
        raise PermissionDenied("You do not have permission to view this organization's invitations.")
    
    return render(request, 'organizations/customize/customize_workspace.html',{'organization':organization})






