from django.shortcuts import render,redirect,get_object_or_404
from accounts.models import(Organization, Profile, EmailInvitation)
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import re
from django.db.models import Count
from organization_channels.models import Message, Link,Channel,ChannelEvents,ActivityChannel
from accounts.models import MeetingOrganization
from django.contrib.auth import authenticate
from django.utils.timezone import now, make_aware
from django.utils.dateparse import parse_datetime

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




# Analytics Overview
import os

def get_file_size(file_field):
    """Returns the size of the file field if it's not empty."""
    if file_field and hasattr(file_field, 'path'):
        return os.path.getsize(file_field.path)  # Returns size in bytes
    return 0


def organization_analytics(request, org_id):
    try:
        # Fetch the organization and check if it exists
        organization = Organization.objects.get(id=org_id)
        profile = get_object_or_404(Profile, user=request.user, organization=organization)
        if not Profile.objects.filter(user=request.user, organization=organization, is_admin=True).exists():
            return JsonResponse({"success": False, "error": "You are not authorized to update the workspace icon."}, status=403)

        print(f"Organization {org_id} found: {organization.name}")

        # 1. Total Storage Used (Messages, Videos, Audio, Links)
        total_messages = Message.objects.filter(organization=organization)
        print(f"Total messages: {total_messages.count()}")

        total_videos = Message.objects.filter(organization=organization).exclude(video__isnull=True)
        print(f"Total videos: {total_videos.count()}")

        total_audio = Message.objects.filter(organization=organization).exclude(audio__isnull=True)
        print(f"Total audio: {total_audio.count()}")

        total_links = Link.objects.filter(organization=organization)
        print(f"Total links: {total_links.count()}")

        # Calculate total storage used
        total_storage_used = 0
        
        # Get all messages and sum the sizes
        total_messages = Message.objects.filter(organization=organization)
        
        for message in total_messages:
            total_storage_used += get_file_size(message.content)  # Add content size
            total_storage_used += get_file_size(message.video)  # Add video size
            total_storage_used += get_file_size(message.audio)  # Add audio size
        
        # Get all links and sum the sizes
        total_links = Link.objects.filter(organization=organization)
        for link in total_links:
            total_storage_used += get_file_size(link.file)  # If Link model has a file field
            
        # You can also calculate the size for other fields as needed
        
        print(f"Total storage used (in bytes): {total_storage_used}")
        
        # Convert to MB for easier reading
        total_storage_used_mb = total_storage_used / (1024 * 1024)
        print(f"Total storage used (in MB): {total_storage_used_mb}")
        
        # 2. Total Channels (Public/Private)
        total_channels = Channel.objects.filter(organization=organization)
        print(f"Total channels: {total_channels.count()}")

        public_channels = total_channels.filter(visibility='PUBLIC')
        print(f"Public channels: {public_channels.count()}")

        private_channels = total_channels.filter(visibility='PRIVATE')
        print(f"Private channels: {private_channels.count()}")

        # 3. Total Messages Sent in All Channels
        total_messages_sent = total_messages.count()
        print(f"Total messages sent: {total_messages_sent}")

        # 4. Total Members (Profiles linked to the organization)
        total_members = Profile.objects.filter(organization=organization).count()  
        print(f"Total members: {total_members}")

        # 5. Total Active Users (Users who sent messages or interacted)
        active_users = total_messages.values('user').distinct().count()
        print(f"Active users: {active_users}")

        # 6. Total Events
        total_events = ChannelEvents.objects.filter(organization=organization).count()
        print(f"Total events: {total_events}")

        # 7. Total Meetings
        total_meetings = MeetingOrganization.objects.filter(organization=organization).count()
        print(f"Total meetings: {total_meetings}")

        # 8. Messages Pinned
        total_pinned_messages = total_messages.filter(is_pinned=True).count()
        print(f"Total pinned messages: {total_pinned_messages}")

        # 9. Messages Starred
        total_starred_messages = total_messages.filter(is_starred=True).count()
        print(f"Total starred messages: {total_starred_messages}")

        # 10. Abused Messages Reported
        total_abused_messages = ActivityChannel.objects.filter(organization=organization, action_type='WARN').count()
        print(f"Total abused messages: {total_abused_messages}")

        # Debugging output to check all results
        print(f"Context data: {locals()}")

        # Render the template with context
        context = {
            'organization': organization,
            'total_storage_used': total_storage_used,
            'total_channels': total_channels.count(),
            'public_channels': public_channels.count(),
            'private_channels': private_channels.count(),
            'total_messages_sent': total_messages_sent,
            'total_members': total_members,
            'active_users': active_users,
            'total_events': total_events,
            'total_meetings': total_meetings,
            'total_pinned_messages': total_pinned_messages,
            'total_starred_messages': total_starred_messages,
            'total_abused_messages': total_abused_messages,
        }

        return render(request, 'organizations/analytics/analytics.html', context)

    except Organization.DoesNotExist:
        print(f"Organization with ID {org_id} does not exist.")
        context = {
            'error_message': "Organization not found."
        }
        return render(request, 'organizations/analytics/analytics.html', context)

    except Exception as e:
        print(f"Error: {str(e)}")
        context = {
            'error_message': f"An error occurred: {str(e)}"
        }
        return render(request, 'organizations/analytics/analytics.html', context)



# Organization Details
def organization_details(request, org_id):
    try:
        # Fetch the organization by ID
        print(f"Fetching organization with ID: {org_id}")
        organization = Organization.objects.get(id=org_id)
        profile = get_object_or_404(Profile, user=request.user, organization=organization)
        if not Profile.objects.filter(user=request.user, organization=organization, is_admin=True).exists():
            return JsonResponse({"success": False, "error": "You are not authorized to update the workspace icon."}, status=403)

        print(f"Organization fetched: {organization.name}")

        # Fetch the admin profile for the organization
        admin_profile = Profile.objects.get(organization=organization, is_admin=True)
        print(f"Admin profile found: {admin_profile.full_name}")

        # Check if organization has an icon, else use a default
        org_icon = organization.icon.url if organization.icon else 'default_icon.png'
        print(f"Organization icon: {org_icon}")

        # Prepare static data for Retention & Exports section
        retention_text = {
            'messages': 'Messages are kept for 1 year. Edit history and messages deleted by people or apps are never saved.',
            'files': 'Files are kept for 1 year. Files deleted by people or apps are never saved.',
            'canvases_lists': 'Canvases and lists are kept for 1 year. Canvases and lists deleted by people or apps are never saved.',
            'export_access': 'Public data can be exported. Workspace owners and admins can export messages and files from public channels.'
        }
        print(f"Retention and export information loaded.")

        # Render the template with context data
        context = {
            'organization': organization,
            'admin_profile': admin_profile,
            'org_icon': org_icon,
            'retention_text': retention_text,
        }
        print("Rendering template with context data.")

        return render(request, 'organizations/details/organization_details.html', context)

    except Organization.DoesNotExist:
        print(f"Organization with ID {org_id} does not exist.")
        context = {
            'error_message': "Organization not found."
        }
        return render(request, 'organizations/details/organization_details.html', context)

    except Profile.DoesNotExist:
        print(f"Admin profile not found for organization with ID {org_id}.")
        context = {
            'error_message': "Admin profile not found or the organization does not have an admin."
        }
        return render(request, 'organizations/details/organization_details.html', context)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        context = {
            'error_message': f"An error occurred: {str(e)}"
        }
        return render(request, 'organizations/details/organization_details.html', context)


# Transfer ownership


@login_required
def fetch_organization_members(request, org_id):
    organization = get_object_or_404(Organization, id=org_id)

    profile = get_object_or_404(Profile, user=request.user, organization=organization)
    if not Profile.objects.filter(user=request.user, organization=organization, is_admin=True).exists():
        return JsonResponse({"success": False, "error": "You are not authorized to update the workspace icon."}, status=403)

    current_admin = get_object_or_404(Profile, user=request.user, organization=organization, is_admin=True)

    # Get search query from GET parameters
    email_search = request.GET.get('email', '').strip()

    if email_search:
        members = Profile.objects.filter(organization=organization, user__email__icontains=email_search).select_related('user')
    else:
        members = Profile.objects.filter(organization=organization).select_related('user')

    context = {
        'organization': organization,
        'members': members,
        'email_search': email_search  
    }

    return render(request, 'organizations/details/transfer_ownership.html', context)



# HANDLE TRANSFER OWNERSHIP

@login_required
def transfer_ownership(request, org_id, member_id):
    if request.method == "POST":
        
        current_admin = get_object_or_404(Profile, organization_id=org_id, user=request.user, is_admin=True)
        organization = get_object_or_404(Organization, id=org_id)
        profile = get_object_or_404(Profile, user=request.user, organization=organization)
        if not Profile.objects.filter(user=request.user, organization=organization, is_admin=True).exists():
            return JsonResponse({"success": False, "error": "You are not authorized to update the workspace icon."}, status=403)

        new_admin = get_object_or_404(Profile, organization_id=org_id, user_id=member_id)

        # Validate password
        password = request.POST.get("password")
        if not authenticate(username=request.user.username, password=password):
            return JsonResponse({"error": "Invalid password"}, status=400)

        if new_admin.user == current_admin.user:
            return JsonResponse({"error": "You cannot transfer ownership to yourself"}, status=400)

        current_admin.is_admin = False
        current_admin.is_manager = True  
        current_admin.save()

        new_admin.is_admin = True
        new_admin.is_manager = False
        new_admin.is_employee = False
        new_admin.save()

        return JsonResponse({"success": "Ownership transferred successfully"})

    return JsonResponse({"error": "Invalid request"}, status=400)


# DELETE THE WORKSPACE

@login_required
def delete_workspace(request, org_id):
    if request.method == "POST":
       
        organization = get_object_or_404(Organization, id=org_id)
        profile = get_object_or_404(Profile, user=request.user, organization=organization)
        if not Profile.objects.filter(user=request.user, organization=organization, is_admin=True).exists():
            return JsonResponse({"success": False, "error": "You are not authorized to update the workspace icon."}, status=403)

        current_admin = get_object_or_404(Profile, organization=organization, user=request.user, is_admin=True)

       
        password = request.POST.get("password")
        if not password:
            return JsonResponse({"error": "Password is required"}, status=400)
        
        user = authenticate(username=request.user.username, password=password)
        if not user:
            return JsonResponse({"error": "Invalid password"}, status=400)
        
       
        if current_admin.user != request.user:
            return JsonResponse({"error": "You are not authorized to delete this workspace"}, status=403)

        try:
          
            organization.delete()
            return JsonResponse({"success": "Workspace deleted successfully"})
        
        except Exception as e:
            
            return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)


# USER GROUPS


@login_required
def fetch_organization_groups(request, org_id):
    organization = get_object_or_404(Organization, id=org_id)

    profile = get_object_or_404(Profile, user=request.user, organization=organization)
    if not Profile.objects.filter(user=request.user, organization=organization, is_admin=True).exists():
        return JsonResponse({"success": False, "error": "You are not authorized to view the groups."}, status=403)

    groups = organization.groups.all()[:4]  

    context = {
        'organization': organization,
        'groups': groups
    }

    return render(request, 'organizations/groups/view_groups.html', context)



# VIEW INVITATIONS
from django.utils import timezone


@login_required
def view_invitations(request, org_id):
  
    organization = get_object_or_404(Organization, id=org_id)
    profile = get_object_or_404(Profile, user=request.user, organization=organization)
    if not Profile.objects.filter(user=request.user, organization=organization, is_admin=True).exists():
        return JsonResponse({"success": False, "error": "You are not authorized to view the groups."}, status=403)

    
   
    if not Profile.objects.filter(user=request.user, organization=organization).exists():
        return JsonResponse({"error": "You are not a member of this organization"}, status=403)

 
    invitations = EmailInvitation.objects.filter(organization=organization)

    
    accepted_invitations = invitations.filter(status='accepted')
    rejected_invitations = invitations.filter(status='rejected')
    pending_invitations = invitations.filter(status='pending')
    expired_invitations = invitations.filter(expires_at__lt=timezone.now(), status='pending')

 
    search_email = request.GET.get('search_email', '')
    if search_email:
        invitations = invitations.filter(invitee_email__icontains=search_email)
    else:
        invitations = invitations.all()

    context = {
        'organization': organization,
        'accepted_invitations': accepted_invitations,
        'rejected_invitations': rejected_invitations,
        'pending_invitations': pending_invitations,
        'expired_invitations': expired_invitations,
        'search_email': search_email
    }

    return render(request, 'organizations/invitations/view_invitations.html', context)


# PREVENT INVITATIONS

@login_required
def delete_invitation(request, org_id, invitation_id):
    if request.method == "POST":
        organization = get_object_or_404(Organization, id=org_id)
        
        # Ensure the user is an admin
        if not Profile.objects.filter(user=request.user, organization=organization, is_admin=True).exists():
            return JsonResponse({"success": False, "error": "You are not authorized to delete invitations."}, status=403)

        invitation = get_object_or_404(EmailInvitation, id=invitation_id, organization=organization)
        invitation.delete()
        
        return JsonResponse({"success": True, "message": "Invitation deleted successfully!"})
    
    return JsonResponse({"success": False, "error": "Invalid request."}, status=400)


# EXTEND INVITATION EXPIRY

@login_required
def extend_invitation_expiry(request, org_id, invitation_id):
    """Allow admin to extend invitation expiry date."""
    organization = get_object_or_404(Organization, id=org_id)
    invitation = get_object_or_404(EmailInvitation, id=invitation_id, organization=organization)

    # Check if user is an admin
    profile = Profile.objects.filter(user=request.user, organization=organization, is_admin=True).first()
    if not profile:
        return JsonResponse({"error": "You do not have permission to extend invitations."}, status=403)

    if request.method == "POST":
        new_expiry = request.POST.get("new_expiry")
        if not new_expiry:
            return JsonResponse({"error": "Invalid date provided."}, status=400)

        try:
            new_expiry_datetime = parse_datetime(new_expiry)
            if new_expiry_datetime:
                new_expiry_datetime = make_aware(new_expiry_datetime)

            if not new_expiry_datetime or new_expiry_datetime <= now():
                return JsonResponse({"error": "Expiry date must be in the future."}, status=400)

            invitation.expires_at = new_expiry_datetime
            invitation.save()

            return JsonResponse({"success": True, "message": "Invitation expiry extended successfully."})

        except Exception as e:
            return JsonResponse({"error": f"Error: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=400)



# Billing section
from datetime import datetime


@login_required
def workspace_billing(request, org_id):
    organization = get_object_or_404(Organization, id=org_id)

    # Check if the user has access to the organization
    if not Profile.objects.filter(user=request.user, organization=organization).exists():
        return render(request, 'organizations/no_access.html')

    # Fetch all members for "Member Changes" section
    members = Profile.objects.filter(organization=organization)

    # Generate dummy activity logs for now (can be replaced with real tracking later)
    member_changes = [
        {
            "name": member.user.username,
            "email": member.user.email,
            "profile_picture": member.profile_picture.url if member.profile_picture else None,
            "date": datetime.now().strftime("%B %Y"),  # Example: "January 2025"
            "status": "was detected as active"
        }
        for member in members
    ]

    context = {
        "organization": organization,
        "billing_email": request.user.email,
        "members": members,
        "member_changes": member_changes
    }

    return render(request, "organizations/billing/billing.html", context)



# Workflow and templates

def workflow_template(request, org_id):
    organization=get_object_or_404(Organization, id=org_id)
    return render(request, 'organizations/billing/workflows.html',{'organization':organization})



