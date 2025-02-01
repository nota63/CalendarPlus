from django.shortcuts import render,redirect,get_object_or_404
from accounts.models import(Organization, Profile, EmailInvitation)
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import re
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
    
    return render(request, 'organizations/customize/customize_workspace.html',{'organization':organization,'profile':profile})



# Actions


# Upload an icon for workspace

@csrf_exempt
def update_workspace_icon(request, org_id):
    if request.method == "POST" and request.FILES.get("icon"):
        organization = get_object_or_404(Organization, id=org_id)

      
        if not Profile.objects.filter(user=request.user, organization=organization, is_admin=True).exists():
            return JsonResponse({"success": False, "error": "You are not authorized to update the workspace icon."}, status=403)

      
        icon_file = request.FILES["icon"]

        
        if organization.icon and organization.icon.name:  
            if default_storage.exists(organization.icon.path): 
                default_storage.delete(organization.icon.path)

        
        organization.icon = icon_file  
        organization.save()

        return JsonResponse({"success": True, "message": "Workspace icon updated successfully!", "icon_url": organization.icon.url})

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)



# Set Workspace Status
import json

@csrf_exempt
def update_organization_status(request, org_id):
    if request.method == 'POST':
       
        organization = get_object_or_404(Organization, id=org_id)

        if not Profile.objects.filter(user=request.user, organization=organization, is_admin=True).exists():
            return JsonResponse({"success": False, "error": "You are not authorized to update the workspace icon."}, status=403)

        try:
            data = json.loads(request.body)
            new_status = data.get('status')
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON format."}, status=400)

        status_choices = dict(Organization.STATUS_CHOICES)
        if new_status not in status_choices:
            return JsonResponse({"success": False, "error": "Invalid status."}, status=400)

       
        organization.status = new_status
        organization.save()

        return JsonResponse({"success": True, "message": "Organization status updated successfully!"})

    return JsonResponse({"success": False, "error": "Invalid request method."}, status=400)



# Edit Profile

@login_required
def edit_profile(request, org_id):
    
    organization = get_object_or_404(Organization, id=org_id)
    profile = get_object_or_404(Profile, user=request.user, organization=organization)
    if not Profile.objects.filter(user=request.user, organization=organization, is_admin=True).exists():
            return JsonResponse({"success": False, "error": "You are not authorized to update the workspace icon."}, status=403)

    
    if request.method == "GET":
        
        data = {
            'full_name': profile.full_name,
            'profile_picture': profile.profile_picture.url if profile.profile_picture else None,
            'email': request.user.email,
        }
        return JsonResponse({'success': True, 'data': data})

    elif request.method == "POST":
    
        full_name = request.POST.get('full_name')
        profile_picture = request.FILES.get('profile_picture')
        email = request.POST.get('email')

      
        if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return JsonResponse({"success": False, "error": "Invalid email format."}, status=400)

        
        if email:
            request.user.email = email
            request.user.save()

        profile.full_name = full_name if full_name else profile.full_name
        if profile_picture:
            profile.profile_picture = profile_picture
        profile.save()

        return JsonResponse({"success": True, "message": "Profile updated successfully!"})

    return JsonResponse({"success": False, "error": "Invalid request method."}, status=400)




