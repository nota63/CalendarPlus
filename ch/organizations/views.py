from django.shortcuts import render,redirect,get_object_or_404
from accounts.models import(Organization, Profile, EmailInvitation, Suspend,MeetingOrganization,Availability,MeetingReminder)
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import re
from django.db.models import Count, Avg, Sum, F, ExpressionWrapper, DurationField
from organization_channels.models import Message, Link,Channel,ChannelEvents,ActivityChannel
from django.contrib.auth import authenticate
from django.utils.timezone import now, make_aware
from django.utils.dateparse import parse_datetime
from .models import OrganizationHide
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from datetime import timedelta
import holidays
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views import View
from accounts.models import Organization,Profile
from django.utils.timezone import now
from django.db.models import Q,F,When
from groups.models import Group,GroupMember,GroupInvitation,GroupEvent,GroupEventBooking
from group_tasks.models import Task, AddDay
from django.template.loader import render_to_string
import dateparser  
from django.utils.html import strip_tags
from accounts.models import ProjectEmployeeAssignment, Project, ProjectManagerAssignment
from groups.models import Group, GroupMember
import logging
from .models import RecurringMeeting,Help,OrganizationProtection,TrackAccess
from django.views.decorators.http import require_http_methods
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import check_password
import base64
import os
from django.utils.timezone import localtime
# Load the same SECRET_KEY used in models
from django.conf import settings

# Configure logging for debugging
logger = logging.getLogger(__name__)


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





# Hide Organization

@login_required
def hide_organization(request, org_id):
    organization = get_object_or_404(Organization, id=org_id)

    if request.method == "POST":
        hidden_from = request.POST.get('hidden_from')
        hidden_until = request.POST.get('hidden_until')
        
      
        hide_on_sundays_and_holidays = request.POST.get('hide_on_sundays_and_holidays') == 'on'

        if hidden_from and hidden_until:
           
            hide_info = OrganizationHide.objects.create(
                from_organization=organization,
                to_organization=organization,
                hidden_from=hidden_from,
                hidden_until=hidden_until,
                hider=request.user,  
                hide_on_sundays_and_holidays=hide_on_sundays_and_holidays 
            )

            
            staff_profiles = Profile.objects.filter(organization=organization, is_employee=True, is_manager=True)

           
          
            staff_emails = [profile.user.email for profile in staff_profiles]

            send_mail(
                'Organization Hidden Notification',
                f'Hello,\n\nThe organization "{organization.name}" has been temporarily hidden from view. It will remain hidden from {hidden_from} to {hidden_until}.',
                settings.DEFAULT_FROM_EMAIL,
                staff_emails,
                fail_silently=False,
            )

            
            if hide_on_sundays_and_holidays:
               
                hidden_from_datetime = datetime.strptime(hidden_from, '%Y-%m-%dT%H:%M')  
                hidden_until_datetime = datetime.strptime(hidden_until, '%Y-%m-%dT%H:%M')  
                
                
                if hidden_from_datetime.weekday() == 6 or hidden_from_datetime in holidays.CountryHoliday('US'):
                    hidden_from_datetime += timedelta(days=1)  
                
              
                hide_info.hidden_from = hidden_from_datetime
                hide_info.hidden_until = hidden_until_datetime
                hide_info.save()

            messages.success(request,f'{organization.name} hidden successfully')

    return render(request, 'organizations/details/hide_organization.html', {'organization': organization})



# Handle workspace duplication


logger = logging.getLogger(__name__)

@method_decorator(login_required, name='dispatch')
class DuplicateWorkspaceView(View):
    def post(self, request, org_id):
        """Handles workspace duplication based on admin's selected options."""
        admin_profile = Profile.objects.filter(user=request.user, organization_id=org_id, is_admin=True).first()
        if not admin_profile:
            return JsonResponse({'error': 'Only admins can duplicate workspaces'}, status=403)

        organization = get_object_or_404(Organization, id=org_id)
        options = request.POST.getlist('options')  # List of things to duplicate

        # If "everything" is selected, duplicate all entities
        if 'everything' in options:
            options = ['workspace_with_members', 'projects', 'meetings', 'channels', 'groups']

        try:
            with transaction.atomic():
                # Create a new workspace
                new_org = Organization.objects.create(
                    name=f"{organization.name} (Copy)",
                    description=organization.description,
                    icon=organization.icon,
                    status=organization.status
                )
                
                logger.info(f"Duplicated organization: {new_org}")

                # Ensure the creator becomes an admin in the new organization
                admin_profile_new = Profile.objects.create(
                    user=request.user,
                    organization=new_org,
                    is_admin=True,
                    is_manager=False,
                    is_employee=False,
                    full_name=request.user.get_full_name()
                )

                # Dictionary to track old users → new profiles
                user_mapping = {request.user: admin_profile_new}

              
                if 'workspace_with_members' in options:
                    members = Profile.objects.filter(organization=organization).exclude(user=request.user)
                    for member in members:
                        new_member = Profile.objects.create(
                            user=member.user,
                            organization=new_org,
                            is_admin=member.is_admin,
                            is_manager=member.is_manager,
                            is_employee=member.is_employee,
                            profile_picture=member.profile_picture,
                            full_name=member.full_name
                        )
                        user_mapping[member.user] = new_member  
                    logger.info("Duplicated members successfully.")

                # Duplicate projects
                if 'projects' in options:
                    old_projects = Project.objects.filter(organization=organization)
                    for project in old_projects:
                        creator_profile = user_mapping.get(project.created_by.user, admin_profile_new)
                        new_project = Project.objects.create(
                            name=project.name,
                            description=project.description,
                            start_date=project.start_date,
                            end_date=project.end_date,
                            organization=new_org,
                            created_by=creator_profile
                        )

                        # Duplicate project managers
                        old_managers = ProjectManagerAssignment.objects.filter(project=project)
                        for manager in old_managers:
                            if manager.manager.user in user_mapping:
                                ProjectManagerAssignment.objects.create(
                                    project=new_project,
                                    manager=user_mapping[manager.manager.user]
                                )

                        # Duplicate employee assignments
                        old_employees = ProjectEmployeeAssignment.objects.filter(project=project)
                        for employee in old_employees:
                            if employee.employee.user in user_mapping and employee.manager.user in user_mapping:
                                ProjectEmployeeAssignment.objects.create(
                                    project=new_project,
                                    employee=user_mapping[employee.employee.user],
                                    manager=user_mapping[employee.manager.user]
                                )
                    logger.info("Duplicated projects successfully.")

                # Duplicate meetings
                if 'meetings' in options:
                    meetings = MeetingOrganization.objects.filter(organization=organization)
                    for meeting in meetings:
                        new_meeting = MeetingOrganization.objects.create(
                            organization=new_org,
                            user=user_mapping.get(meeting.user, admin_profile_new),
                            invitee=user_mapping.get(meeting.invitee, admin_profile_new),
                            meeting_title=meeting.meeting_title,
                            meeting_description=meeting.meeting_description,
                            meeting_date=meeting.meeting_date,
                            start_time=meeting.start_time,
                            end_time=meeting.end_time,
                            meeting_link=meeting.meeting_link,
                            meeting_location=meeting.meeting_location,
                            meeting_type=meeting.meeting_type,
                            status=meeting.status,
                            is_notification_sent=meeting.is_notification_sent
                        )
                        new_meeting.participants.set([
                            user_mapping.get(participant, admin_profile_new) for participant in meeting.participants.all()
                        ])
                    logger.info("Duplicated meetings successfully.")

                # Duplicate channels
                if 'channels' in options:
                    channels = Channel.objects.filter(organization=organization)
                    for channel in channels:
                        new_channel = Channel.objects.create(
                            organization=new_org,
                            created_by=request.user,
                            name=channel.name,
                            type=channel.type,
                            visibility=channel.visibility
                        )
                        new_channel.allowed_members.set([
                            user_mapping.get(member, admin_profile_new) for member in channel.allowed_members.all()
                        ])
                    logger.info("Duplicated channels successfully.")

                # Duplicate groups
                # Duplicate groups
                if 'groups' in options:
                    groups = Group.objects.filter(organization=organization)
                    for group in groups:
                        new_group = Group.objects.create(
                           organization=new_org,
                           name=group.name,
                           description=group.description,
                           team_leader=user_mapping.get(group.team_leader, request.user).user,  
                          created_by=user_mapping.get(group.created_by, request.user).user  
                     )
        
                   # Duplicate group members (inside the loop)
                    group_members = GroupMember.objects.filter(group=group)
                    for member in group_members:
                        if member.user in user_mapping:
                            GroupMember.objects.create(
                            group=new_group,
                             organization=new_org,
                            user=user_mapping[member.user].user,  
                            role=member.role
                        )
        
                        logger.info("Duplicated groups successfully.")


                return JsonResponse({'message': 'Workspace duplicated successfully!', 'new_org_id': new_org.id}, status=200)

        except Exception as e:
            logger.error(f"Error duplicating workspace: {e}")
            return JsonResponse({'error': 'Failed to duplicate workspace'}, status=500)
        


# PULSE FEATURES

from accounts.models import EventOrganization
from django.contrib.auth.models import User

def get_last_two_activities(org_id):
    """Fetch last two activities of all unique members in an organization."""
    
    users = User.objects.filter(profiles__organization=org_id).distinct()
    organization = get_object_or_404(Organization, id=org_id)
    



    activity_data = {}

    for user in users:
        activities = []

       
        activities += list(
            Message.objects.filter(user=user).values(activity=F("content"), activity_time=F("timestamp"))
        ) + list(
            GroupEvent.objects.filter(created_by=user).values(activity=F("title"), activity_time=F("created_at"))
        ) + list(
            MeetingOrganization.objects.filter(user=user).values(activity=F("meeting_title"), activity_time=F("created_at"))
        ) + list(
            EventOrganization.objects.filter(user=user).values(activity=F("title"), activity_time=F("created_at"))
        ) + list(
            Task.objects.filter(assigned_to=user).values(activity=F("title"), activity_time=F("created_at"))
        ) + list(
            Group.objects.filter(created_by=user).values(activity=F("name"), activity_time=F("created_at"))
        ) + list(
            Channel.objects.filter(created_by=user).values(activity=F("name"), activity_time=F("created_at"))
        ) + list(
            GroupEventBooking.objects.filter(user=user).values(activity=F("group_event"), activity_time=F("created_at"))
        )

      
        activities = [act for act in activities if act.get("activity_time")]

       
        activities = sorted(activities, key=lambda x: x["activity_time"], reverse=True)[:2]

        activity_data[user.username] = activities  

    return activity_data


def organization_pulse_view(request, org_id):
    """View to render the pulse page showing member activities."""
    organization=get_object_or_404(Organization, id=org_id)
    
    user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
    if not user_profile:
        return JsonResponse({'error': 'You are not part of this organization.'}, status=403)


    
  
    if not Profile.objects.filter(organization=organization).exists():
        return render(request, "pulse.html", {"error": "No members found in this organization."})

      
    time_slots = [
        "12 AM", "1 AM", "2 AM", "3 AM", "4 AM", "5 AM", "6 AM", "7 AM",
        "8 AM", "9 AM", "10 AM", "11 AM", "12 PM", "1 PM", "2 PM", "3 PM",
        "4 PM", "5 PM", "6 PM", "7 PM", "8 PM", "9 PM", "10 PM", "11 PM"
    ] 

    activity_data = get_last_two_activities(org_id)
    
    return render(request, "organizations/pulse/pulse.html", {"activity_data": activity_data,'organization':organization,'profile':Profile,'time_slots':time_slots})



# PULSE SETTINGS 
def pulse_settings(request, org_id):
    organization=get_object_or_404(Organization, id=org_id)
    
    user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
    if not user_profile:
        return JsonResponse({'error': 'You are not part of this organization.'}, status=403)


    development = [
        {"title": "Custom Fields", "description": "Enhance your workspace by adding custom fields..."},
        {"title": "Dependency Warning", "description": "Get alerts when task dependencies are not met..."},
        {"title": "Email", "description": "Enable email notifications for important updates..."},
        {"title": "Incomplete Warning", "description": "Receive warnings for incomplete tasks..."},
        {"title": "Remap Subtask Due Dates", "description": "Automatically adjust subtask due dates..."},
        {"title": "Reschedule Dependencies", "description": "Adjust dependent task deadlines..."},
    ]

    work_in_progress = [
        {"title": "Work in Progress Limits", "description": "Set limits on active tasks to prevent overload..."}
    ]

    space = [
        {"title": "Show Status Progress", "description": "Track the real-time progress of tasks..."},
        {"title": "Tags", "description": "Categorize and organize tasks effectively..."},
        {"title": "Time Estimates", "description": "Set estimated time for tasks and projects..."}
    ]

    return render(request, "organizations/pulse/pulse_settings.html", {
        "development": development,
        "work_in_progress": work_in_progress,
        "space": space,
        'organization':organization,
    })


# SUSPEND THE USER FROM WORKSPACE


# FETCH MEMBERS FIRST 
@login_required
def handle_suspend_action(request, org_id, user_id=None, action=None):
    organization = get_object_or_404(Organization, id=org_id)

    admin_profile = Profile.objects.filter(user=request.user, organization_id=org_id, is_admin=True).first()
    if not admin_profile:
        return JsonResponse({'error': 'Only admins can perform this action!'}, status=403)


   
    if request.method == "GET":
        members = Profile.objects.filter(organization=organization).select_related("user")
        suspended_users = Suspend.objects.filter(organization=organization, is_suspended=True).values_list("user_id", flat=True)

        members_data = [
            {
                "id": member.user.id,
                "name": member.user.username,
                "role": "Admin" if member.is_admin else "Manager" if member.is_manager else "Employee",
                "is_suspended": member.user.id in suspended_users  
            }
            for member in members
        ]

        return JsonResponse({"status": "success", "members": members_data})

    # 🔥 Handling Ban/Unban Actions
    if request.method == "POST" and user_id and action:
        user = get_object_or_404(User, id=user_id)
        admin = request.user  

        if action == "ban":
            reason = request.POST.get("reason", "No reason provided")
            suspend_obj, created = Suspend.objects.get_or_create(
                user=user,
                organization=organization,
                defaults={"suspended_by": admin, "reason": reason, "suspended_at": timezone.now(), "is_suspended": True}
            )

            if not created:
                suspend_obj.ban(admin, reason)

            return JsonResponse({"status": "success", "message": f"{user.username} has been suspended."})

        elif action == "unban":
            suspend_obj = Suspend.objects.filter(user=user, organization=organization, is_suspended=True).first()
            if suspend_obj:
                suspend_obj.unban()
                return JsonResponse({"status": "success", "message": f"{user.username} has been unsuspended."})

        return JsonResponse({"status": "error", "message": "Invalid action."}, status=400)

    return JsonResponse({"status": "error", "message": "Invalid request."}, status=400)


# MEETING CREATION VIA NLP (NATURAL LANGUAGE PROCESSING)

@csrf_exempt
def create_meeting_from_nlp(request, org_id):
    """
    Handles meeting creation from natural language input.
    Example Input: "Schedule a meeting with John tomorrow at 3 PM"
    """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)
        input_text = data.get("input_text")

        print("INPUT TEXT :",input_text)

        if not input_text:
            return JsonResponse({"error": "Missing required fields"}, status=400)

        # Validate Organization
        organization = get_object_or_404(Organization, id=org_id)

        
        user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
        if not user_profile:
           return JsonResponse({'error': 'You are not part of this organization.'}, status=403)



        # Validate User (Requester)
        user = request.user
        user_profile = Profile.objects.filter(user=user, organization=organization).first()
        if not user_profile:
            return JsonResponse({"error": "You are not part of this organization"}, status=403)

        # 🔥 Custom NLP Date Extraction
        meeting_datetime = extract_datetime_from_text(input_text)
        if not meeting_datetime:
            return JsonResponse({"error": "Could not understand date/time. Please use a format like 'tomorrow at 3 PM'."}, status=400)

        meeting_date = meeting_datetime.date()
        start_time = meeting_datetime.time()
        end_time = (datetime.combine(meeting_date, start_time) + timedelta(hours=1)).time()  

        # Extract Invitee and check if they belong to the same organization
        invitee_username = extract_invitee_from_text(input_text)

        if invitee_username:
           invitee_username = invitee_username.lower()  
           invitee = User.objects.filter(username__iexact=invitee_username).first()  

           if invitee:
             invitee_profile = Profile.objects.filter(user=invitee, organization=organization).exists()
             if not invitee_profile:
                return JsonResponse({"error": f"{invitee_username} is not in this organization"}, status=400)
        else:
            return JsonResponse({"error": f"User {invitee_username} not found"}, status=400)


        # Check for scheduling conflicts
        if invitee:
            conflict = MeetingOrganization.objects.filter(
                organization=organization,
                meeting_date=meeting_date,
                start_time=start_time,
                participants=invitee
            ).exists()

            if conflict:
                return JsonResponse({"error": f"{invitee_username} is already booked at this time"}, status=400)
            
            # Convert meeting date to weekday index (0 = Monday, 6 = Sunday)
         
            # ✅ Convert meeting date to weekday index (0 = Monday, 6 = Sunday)
#             meeting_weekday = meeting_date.weekday()

# # ✅ Check if an exact unbooked slot exists for the invitee
#             selected_slot = Availability.objects.filter(
#                user=invitee,
#                     organization=organization,
#                day_of_week=meeting_weekday,
#                 start_time=start_time,  # Must match start time exactly
#                 end_time=end_time,  # Must match end time exactly
#                   is_booked=False  # Only check available slots
#               ).first()  # Pick the first match

#             if not selected_slot:
#                return JsonResponse({"error": "Invitee is not available at this time!"}, status=400)

# # ✅ Mark this slot as booked
#             selected_slot.is_booked = True
#             selected_slot.save()

         

        # Create Meeting
        meeting = MeetingOrganization.objects.create(
            organization=organization,
            user=user,
            invitee=invitee,
            meeting_title=f"Meeting with {invitee_username}" if invitee else "New Meeting",
            meeting_date=meeting_date,
            start_time=start_time,
            end_time=end_time,
            status="scheduled",
        )
        send_meeting_email(meeting)
        if invitee:
            meeting.participants.add(invitee)


        return JsonResponse({
            "message": "Meeting created successfully",
            "meeting_id": meeting.id,
            "meeting_date": meeting_date.strftime("%Y-%m-%d"),
            "start_time": start_time.strftime("%H:%M:%S"),
            "end_time": end_time.strftime("%H:%M:%S"),
            "invitee": invitee_username if invitee else None
        })

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=400)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    


# 📌 Helper Function: NLP Date Parsing
def extract_datetime_from_text(text):
    """
    Extracts datetime from text like:
    - "tomorrow at 3 PM"
    - "next Monday at 10 AM"
    """
    text = text.lower()
    now = datetime.now()

    # 🔥 Handle "tomorrow" manually
    if "tomorrow" in text:
        base_date = now + timedelta(days=1)
    elif "next" in text:
        match = re.search(r"next (\w+)", text)
        if match:
            weekday_str = match.group(1)
            weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            if weekday_str in weekdays:
                target_weekday = weekdays.index(weekday_str)
                days_ahead = (target_weekday - now.weekday() + 7) % 7 or 7
                base_date = now + timedelta(days=days_ahead)
            else:
                return None
        else:
            return None
    else:
        base_date = now  # Assume today if no relative date

    # 🔥 Extract time
    time_match = re.search(r"(\d{1,2})(:\d{2})?\s?(am|pm)?", text)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2)[1:]) if time_match.group(2) else 0
        period = time_match.group(3)

        # Convert to 24-hour format
        if period == "pm" and hour < 12:
            hour += 12
        elif period == "am" and hour == 12:
            hour = 0
    else:
        return None  # No valid time found

    return datetime.combine(base_date.date(), datetime.min.time()).replace(hour=hour, minute=minute)


# 📌 Helper Function to Extract Invitee Name
def extract_invitee_from_text(text):
    """
    Extracts the invitee name from the given text.
    Example: "Schedule a meeting with John tomorrow at 3 PM" → returns "John"
    """
    words = text.lower().split()
    if "with" in words:
        index = words.index("with") + 1
        if index < len(words):
            return words[index].capitalize()  
    return None


# send the email to notify 
def send_meeting_email(meeting):
    """ Sends an email notification to the invitee about the scheduled meeting. """

    subject = f"New Meeting Scheduled with {meeting.user.username}"
    
   
    html_message = render_to_string("emails/meeting_invite.html", {
        "invitee": meeting.invitee,
        "creator": meeting.user,
        "organization": meeting.organization,
        "meeting_title": meeting.meeting_title,
        "meeting_date": meeting.meeting_date,
        "start_time": meeting.start_time,
        "end_time": meeting.end_time,
        "mention_nlp": "This meeting was scheduled using NLP.",
    })
    
    plain_message = strip_tags(html_message) 
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [meeting.invitee.email],  
        html_message=html_message,
        fail_silently=False,
    )







# MEETING ANALYTICS 


def meeting_analytics(request, org_id):
    today = datetime.today().date()
    organization = get_object_or_404(Organization, id=org_id)
    
    user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
    if not user_profile:
        return JsonResponse({'error': 'You are not part of this organization.'}, status=403)



    # Total Meetings
    total_meetings = MeetingOrganization.objects.filter(organization_id=org_id).count()
    completed_meetings = MeetingOrganization.objects.filter(organization_id=org_id, status="completed").count()
    canceled_meetings = MeetingOrganization.objects.filter(organization_id=org_id, status="canceled").count()
    upcoming_meetings = MeetingOrganization.objects.filter(organization_id=org_id, meeting_date__gte=today).count()

    # Meeting Types & Modes
    meeting_types = MeetingOrganization.objects.filter(organization_id=org_id).values("meeting_type").annotate(count=Count("id"))
    meeting_modes = MeetingOrganization.objects.filter(organization_id=org_id).values("meeting_location").annotate(count=Count("id"))


    peak_hours = MeetingOrganization.objects.filter(organization_id=org_id).values("start_time").annotate(count=Count("id")).order_by("-count")[:5]

  
    avg_duration = MeetingOrganization.objects.filter(organization_id=org_id).annotate(
        duration=ExpressionWrapper(F("end_time") - F("start_time"), output_field=DurationField())
    ).aggregate(avg_duration=Avg("duration"))["avg_duration"]
    avg_duration = avg_duration.total_seconds() / 3600 if avg_duration else 0  # Convert to hours

 
    top_hosts = (
      MeetingOrganization.objects.filter(organization_id=org_id)
      .annotate(invitee_username=F("invitee__username"))
      .values("invitee_username")
      .annotate(count=Count("id"))
    .order_by("-count")[:5]
   )
  
    avg_attendees = MeetingOrganization.objects.filter(organization_id=org_id).annotate(num_attendees=Count("participants")).aggregate(avg_attendees=Avg("num_attendees"))["avg_attendees"] or 0

    data = {
        "total_meetings": total_meetings,
        "completed_meetings": completed_meetings,
        "canceled_meetings": canceled_meetings,
        "upcoming_meetings": upcoming_meetings,
        "meeting_types": list(meeting_types),
        "meeting_modes": list(meeting_modes),
        "peak_hours": list(peak_hours),
        "avg_duration": round(avg_duration, 2),
        "top_hosts": list(top_hosts),
        "avg_attendees": round(avg_attendees, 2),
    }
    return JsonResponse(data)


# Handle recurring Meetings

@csrf_exempt 
def create_recurring_meeting(request, org_id, user_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            created_by = request.user  

            # Validate Organization and User
            organization = get_object_or_404(Organization, id=org_id)
            
            user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
            if not user_profile:
                return JsonResponse({'error': 'You are not part of this organization.'}, status=403)



            scheduled_user = get_object_or_404(User, id=user_id)  

            # Extract required fields
            recurrence_type = data.get("recurrence_type")
            start_date = data.get("start_date")
            end_date = data.get("end_date", None)
            custom_days = data.get("custom_days", [])
            remind_before = data.get("remind_before", 15)
            send_email_reminder = data.get("send_email_reminder", True)
            send_push_notification = data.get("send_push_notification", True)
            exclude_dates = data.get("exclude_dates", [])

            # Validate recurrence type
            valid_recurrence_types = ["daily", "weekly", "monthly", "yearly", "custom"]
            if recurrence_type not in valid_recurrence_types:
                return JsonResponse({"error": "Invalid recurrence type"}, status=400)

            
            if recurrence_type == "custom" and not isinstance(custom_days, list):
                return JsonResponse({"error": "Custom days must be a list"}, status=400)

            # Convert start_date and end_date to correct format
            try:
                start_date = datetime.fromisoformat(start_date).date() 
                if end_date:
                    end_date = datetime.fromisoformat(end_date).date()
            except ValueError:
                return JsonResponse({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

            # Create recurring meeting
            recurring_meeting = RecurringMeeting.objects.create(
                organization=organization,
                created_by=created_by,
                creator=scheduled_user,  
                recurrence_type=recurrence_type,
                start_date=start_date,
                end_date=end_date,
                custom_days=custom_days if recurrence_type == "custom" else None,
                remind_before=remind_before,
                send_email_reminder=send_email_reminder,
                send_push_notification=send_push_notification,
                exclude_dates=exclude_dates,
            )

            return JsonResponse({"message": "Recurring meeting scheduled successfully!", "meeting_id": recurring_meeting.id}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)



# MANAGE RECURRING MEETINGS

def fetch_recurring_meetings(request, org_id):
    """
    Fetches all recurring meetings created by the logged-in user for a specific organization.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthorized"}, status=401)
    
    organization = get_object_or_404(Organization, id=org_id)
    user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
    if not user_profile:
        return JsonResponse({'error': 'You are not part of this organization.'}, status=403)



    meetings = RecurringMeeting.objects.filter(organization_id=org_id, created_by=request.user)

    meetings_list = [
        {
            "id": meeting.id,
            "type": meeting.type,
            "recurrence_type": meeting.recurrence_type,
            "start_date": meeting.start_date.strftime("%Y-%m-%d"),
            "end_date": meeting.end_date.strftime("%Y-%m-%d") if meeting.end_date else "Indefinite",
            "remind_before": meeting.remind_before,
            "send_email_reminder": meeting.send_email_reminder,
            "send_push_notification": meeting.send_push_notification,
        }
        for meeting in meetings
    ]

    return JsonResponse({"meetings": meetings_list}, status=200)


@csrf_exempt 
def delete_recurring_meeting(request, org_id, meeting_id):
    """
    Deletes a specific recurring meeting if the logged-in user is the creator.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthorized"}, status=401)
    
     
    organization = get_object_or_404(Organization, id=org_id)
    
    user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
    if not user_profile:
        return JsonResponse({'error': 'You are not part of this organization.'}, status=403)


    meeting = get_object_or_404(RecurringMeeting, id=meeting_id, organization_id=org_id, created_by=request.user)
    meeting.delete()

    return JsonResponse({"message": "Meeting deleted successfully"}, status=200)


# MEETINGS CALENDAR 
from django.db import models


@login_required
def get_meetings(request, org_id):
    organization = get_object_or_404(Organization,id=org_id)
    
    user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
    if not user_profile:
        return JsonResponse({'error': 'You are not part of this organization.'}, status=403)

    try:
        
        meetings = MeetingOrganization.objects.filter(
            organization_id=org_id,
        ).filter(
            models.Q(user=request.user) | models.Q(invitee=request.user) | models.Q(participants=request.user)
        ).distinct()

        
        meetings_data = []
        for meeting in meetings:
            meetings_data.append({
                "id": meeting.id,
                "title": meeting.meeting_title,
                "description": meeting.meeting_description,
                "start": f"{meeting.meeting_date}T{meeting.start_time}",
                "end": f"{meeting.meeting_date}T{meeting.end_time}",
                "status": meeting.status,
                "meeting_link": meeting.meeting_link if meeting.meeting_link else "",
                "meeting_type": meeting.meeting_type,
                "meeting_location": meeting.meeting_location,
                "user":meeting.user.username,
                'invitee':meeting.invitee.username
            })
        print("MEETINGS DATA:",meetings_data)    

        return JsonResponse({"meetings": meetings_data}, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)



# MANAGE MEETING REMINDER

@csrf_exempt
def set_meeting_reminder(request, org_id, meeting_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            reminder_time = data.get("reminder_time", 15) 
            custom_minutes = data.get("custom_minutes")
            custom_hours = data.get("custom_hours")
            reminder_type = data.get("reminder_type", "email")
            reminder_style = data.get("reminder_style", "minimalist")
            remind_all_members = data.get("remind_all_members", False)

            organization = get_object_or_404(Organization, id=org_id)
            
            user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
            if not user_profile:
               return JsonResponse({'error': 'You are not part of this organization.'}, status=403)




            meeting = get_object_or_404(MeetingOrganization, id=meeting_id, organization=organization)
            user = request.user  

          
            if reminder_time in [0, 15, 30, 45]:  
                reminder_offset = timedelta(minutes=reminder_time)
            else:  
                reminder_offset = timedelta(minutes=custom_minutes or 0, hours=custom_hours or 0)

            meeting_datetime = datetime.combine(meeting.meeting_date, meeting.start_time)
            reminder_datetime = meeting_datetime - reminder_offset

       
            reminder, created = MeetingReminder.objects.update_or_create(
                organization=organization,
                meeting=meeting,
                user=user,
                defaults={
                    "reminder_type": reminder_type,
                    "reminder_time": reminder_time,
                    "custom_minutes": custom_minutes,
                    "custom_hours": custom_hours,
                    "reminder_datetime": reminder_datetime,
                    "remind_all_members": remind_all_members,
                    "reminder_style": reminder_style,
                }
            )

            return JsonResponse({"message": "Reminder set successfully!", "reminder_id": reminder.id}, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)


# EMBBED CALENDARPLUS

# FILTER MEETINGS BASED ON WORKSPACE AND FOR REQUEST.USER
@login_required
def user_meetings_api(request, org_id):
    organization = get_object_or_404(Organization, id=org_id)
    user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
    if not user_profile:
        return JsonResponse({'error': 'You are not part of this organization.'}, status=403)

    meetings = MeetingOrganization.objects.filter(organization_id=org_id, user=request.user, status="scheduled")

    events = [
        {
            "title": meeting.meeting_title,
            "start": f"{meeting.meeting_date}T{meeting.start_time}",
            "end": f"{meeting.meeting_date}T{meeting.end_time}",
            "url": meeting.meeting_link if meeting.meeting_link else "#",
        }
        for meeting in meetings
    ]

    return JsonResponse(events, safe=False)



# 2️⃣ Generate Embed Code (Iframe + Script)
@login_required
def generate_embed_code(request, org_id):
    organization = get_object_or_404(Organization, id=org_id)
    user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
    if not user_profile:
        return JsonResponse({'error': 'You are not part of this organization.'}, status=403)

    embed_iframe = f"""
    <iframe id="calendar-iframe" src="https://calendarplus.com/embed/{org_id}/" width="100%" height="600" frameborder="0"></iframe>
    """

    embed_script = f"""
    <script>
        function loadCalendar() {{
            var iframe = document.getElementById('calendar-iframe');
            if (iframe) {{
                iframe.src = iframe.src; // Reload to refresh meetings
            }}
        }}
        setInterval(loadCalendar, 300000); // Auto-refresh every 5 minutes
    </script>
    """

    return JsonResponse({"embed_iframe": embed_iframe, "embed_script": embed_script})




# SHUT DOWN ALL MEETINGS
@login_required
def manage_meetings(request, org_id):
    user = request.user  

    organization = get_object_or_404(Organization, id=org_id)
    user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
    if not user_profile:
        return JsonResponse({'error': 'You are not part of this organization.'}, status=403)


    if request.method == "GET":
        """Fetch last 3 meetings before deletion"""
        last_meetings = MeetingOrganization.objects.filter(
            organization_id=org_id
        ).filter(Q(user=user) | Q(invitee=user)).order_by("-created_at")[:3]

        last_meetings_data = [
            {"title": meeting.meeting_title, "date":str(meeting.created_at), "time": str(meeting.start_time)}
            for meeting in last_meetings
        ]

        return JsonResponse({"success": True, "last_meetings": last_meetings_data})

    elif request.method == "POST":
        """Handle password validation and delete meetings"""
        try:
            data = json.loads(request.body)
            password = data.get("password")

            if not password:
                return JsonResponse({"success": False, "message": "❌ Password is required!"}, status=400)

            # Validate password
            if not authenticate(username=user.username, password=password):
                return JsonResponse({"success": False, "message": "❌ Incorrect password!"}, status=400)

      
            deleted_count, _ = MeetingOrganization.objects.filter(
                organization_id=org_id
            ).filter(Q(user=user) | Q(invitee=user)).delete()

        
            send_mail(
                subject="🗑️ Your Meetings Have Been Deleted",
                message=f"Hello {user.get_full_name()},\n\nAll your meetings in this organization have been successfully deleted.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )

            return JsonResponse({
                "success": True,
                "message": f"✅ Deleted {deleted_count} meetings successfully!",
            })

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "❌ Invalid request data!"}, status=400)

    return JsonResponse({"success": False, "message": "❌ Invalid request method!"}, status=400)



# IN APP LIVE MEETINGS


class LaunchRoom(View,LoginRequiredMixin):
    template_name = 'organizations/zeegocloud/initiate_meeting.html'

    def get(self,request, org_id):
        organization = get_object_or_404(Organization, id=org_id)
        user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
        if not user_profile:
            return JsonResponse({'error': 'You are not part of this organization.'}, status=403)

        return render(request, self.template_name,{'organization':organization})
    

# Initiate the live meeting
@login_required
def start_meeting(request,org_id):
    username=request.user.username
    organization = get_object_or_404(Organization, id=org_id)
    user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
    if not user_profile:
        return JsonResponse({'error': 'You are not part of this organization.'}, status=403)

    return render(request,'organizations/zeegocloud/zeego_video.html',{'name':username,'organization':organization})


# Support for transport layer
@login_required
def support_transport_layer(request, org_id):
    organization = get_object_or_404(Organization, id=org_id)
    
    try:
        profile = Profile.objects.get(user=request.user, organization=organization)
    except Profile.DoesNotExist:
        return JsonResponse({'error': 'Profile not found'}, status=404)

    if not profile.is_admin:
        return JsonResponse({'error': 'You are not authorized to perform this action'}, status=403)
    
    return render(request, 'organizations/customize/security_layer.html',{'organization':organization})


# User help queries
@login_required
def user_help_queries(request, org_id):
    """Fetches all help queries raised by the user in the given organization."""
    organization = get_object_or_404(Organization, id=org_id)
    helps = Help.objects.filter(user=request.user, organization=organization).order_by("-created_at")

    # Send only required fields
    data = [
        {
            "id": help.id,
            "title": help.title,
            "help_type": help.get_help_type_display(),
            "priority": help.get_priority_display(),
            "status": help.get_status_display(),
            "created_at": help.created_at.strftime("%Y-%m-%d %H:%M"),
        }
        for help in helps
    ]

    return render(request, "organizations/help/user_help_queries.html", {"helps": data,'organization':organization})


# fetch help details
@login_required
def help_query_details(request, help_id):
    """Fetches full details of a help query."""
    help_query = get_object_or_404(Help, id=help_id, user=request.user)

    data = {
        "title": help_query.title,
        "help_type": help_query.get_help_type_display(),
        "priority": help_query.get_priority_display(),
        "status": help_query.get_status_display(),
        "description": help_query.description,
        "response": help_query.response if help_query.response else "You can get the response directly via email or in CalendarPlus",
        "created_at": help_query.created_at.strftime("%Y-%m-%d %H:%M"),
        "resolved_at": help_query.resolved_at.strftime("%Y-%m-%d %H:%M") if help_query.resolved_at else None,
        "attachment": help_query.attachment.url if help_query.attachment else None,
    }
    
    return JsonResponse(data)


# RAISE HELP QUERY
@login_required
def raise_help_request(request, org_id):
    """Handles user help requests."""
    organization = get_object_or_404(Organization, id=org_id)
    user = request.user

    if request.method == "POST":
        help_type = request.POST.get("help_type")
        title = request.POST.get("title")
        description = request.POST.get("description")
        priority = request.POST.get("priority", "MEDIUM")
        is_anonymous = request.POST.get("is_anonymous") == "true"
        attachment = request.FILES.get("attachment", None)

        if not help_type or not title or not description:
            return JsonResponse({"success": False, "error": "All fields except attachment are required."})

        # Save the help request
        help_request = Help.objects.create(
            user=user if not is_anonymous else None,
            organization=organization,
            help_type=help_type,
            title=title,
            description=description,
            priority=priority,
            attachment=attachment,
            is_anonymous=is_anonymous
        )

        return JsonResponse({"success": True, "message": "Help request submitted successfully!"})

    return JsonResponse({"success": False, "error": "Invalid request method."})


# delete the request
@login_required
def delete_request(request, org_id, help_id):
    organization = get_object_or_404(Organization, id=org_id)
    user_profile = get_object_or_404(Profile, organization=organization, user=request.user)

    if not user_profile.is_admin:
        return HttpResponseForbidden("You are not authorized to delete the requests!")

 
    help_request = get_object_or_404(Help, id=help_id, organization=organization)
    help_request.delete()

    return redirect("user_help_queries", org_id=organization.id)



# ENCRYPT THE WORKSPACE 
def organization_password_settings(request, org_id):
    """Check if password exists, then fetch or render normally"""
    organization = Organization.objects.get(id=org_id)
    org_protection = OrganizationProtection.objects.filter(organization=organization).first()  # Fetch if exists

    context = {
        "organization": organization,
        "protection_status": org_protection.protection_status if org_protection else False,
        "password_exists": bool(org_protection),  # True if protection exists
    }
    return render(request, "organizations/encrypt/organization_password_settings.html", context)


# Set Password AES Protection
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import make_password
from .models import Organization, OrganizationProtection

# 💖 Set Organization Password (Securely)
@csrf_exempt
def set_organization_password(request, org_id):
    """Securely set an organization's password."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            new_password = data.get("password")

            if not new_password or len(new_password) < 6:
                return JsonResponse({"success": False, "message": "Password must be at least 6 characters."})

            organization = Organization.objects.get(id=org_id)
            org_protection, created = OrganizationProtection.objects.get_or_create(organization=organization)

            org_protection.set_password(new_password)  # Use model's hashing method
            org_protection.protection_status = True
            org_protection.save()

            return JsonResponse({"success": True, "message": "Password set successfully!"})

        except ObjectDoesNotExist:
            return JsonResponse({"success": False, "message": "Organization not found."})
        except Exception as e:
            return JsonResponse({"success": False, "message": f"Error: {str(e)}"})

    return JsonResponse({"success": False, "message": "Invalid request method."})

# 💖 Reset Organization Password (Securely)
@csrf_exempt
def reset_organization_password(request, org_id):
    """Securely reset an organization's password."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            new_password = data.get("new_password")

            if not new_password or len(new_password) < 6:
                return JsonResponse({"success": False, "message": "Password must be at least 6 characters."})

            organization = Organization.objects.get(id=org_id)
            org_protection = OrganizationProtection.objects.get(organization=organization)

            org_protection.reset_password(new_password)  # Use model's reset method
            org_protection.save()

            return JsonResponse({"success": True, "message": "Password reset successfully!"})

        except ObjectDoesNotExist:
            return JsonResponse({"success": False, "message": "Organization not found."})
        except Exception as e:
            return JsonResponse({"success": False, "message": f"Error: {str(e)}"})

    return JsonResponse({"success": False, "message": "Invalid request method."})



# MIDDLEWARE REDIRECT & VALIDATE THE PASSWORD

def get_client_ip(request):
    """Extracts the client's IP address"""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip



# VALIDATE WORKSPACE AUTHENTICATION

@login_required
def validate_org_password(request, org_id):
    organization = get_object_or_404(Organization, id=org_id)
    logger.info(f"🔹 Received request for org_id: {org_id}")

    org_protection = get_object_or_404(OrganizationProtection, organization_id=org_id)

    ip_address = get_client_ip(request)
    device_info = request.META.get("HTTP_USER_AGENT", "Unknown Device")

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            entered_password = data.get("password", "").strip()

            if not entered_password:
                logger.warning("⚠️ Empty password entered!")
                return JsonResponse({"success": False, "message": "Password cannot be empty!"})

            if not org_protection.hashed_password:
                logger.error("❌ No password found for this organization!")
                return JsonResponse({"success": False, "message": "No password set for this organization!"})

            if check_password(entered_password, org_protection.hashed_password):
                request.session[f"org_temp_access_{org_id}"] = True
                logger.info("✅ Password matched! Granting temporary access.")

                # Track successful access
                TrackAccess.objects.create(
                    organization=organization,
                    organization_protect=org_protection,
                    user=request.user,
                    access_type="SUCCESS",
                    ip_address=ip_address,
                    device_info=device_info,
                    failed_attempts=0,
                )

                # ✅ Redirect back to the original page user wanted to access
                redirect_url = request.session.pop('org_redirect_after_auth', f"/calendar/org_detail/{org_id}/")
                return JsonResponse({"success": True, "redirect_url": redirect_url})

            logger.warning("❌ Incorrect password entered!")

            failed_attempts = TrackAccess.objects.filter(
                organization=organization, user=request.user, access_type="FAILED"
            ).count() + 1

            # Track failed login
            TrackAccess.objects.create(
                organization=organization,
                organization_protect=org_protection,
                user=request.user,
                access_type="FAILED",
                ip_address=ip_address,
                device_info=device_info,
                failed_attempts=failed_attempts,
            )

            return JsonResponse({"success": False, "message": "Incorrect password!"})

        except json.JSONDecodeError:
            logger.error("❌ Invalid JSON received in request!")
            return JsonResponse({"success": False, "message": "Invalid data format!"})

    return render(request, "organizations/encrypt/validate_org_password.html", {"org_id": org_id, "organization": organization})



















# REMOVE WORKSPACE PASSWORD
@login_required
def remove_org_password(request, org_id):
    """Handle password removal securely"""
    if request.method == "POST":
        try:
            org_protection = get_object_or_404(OrganizationProtection, organization_id=org_id)

            # Check if user is an admin or authorized
            profile = get_object_or_404(Profile, user=request.user, organization_id=org_id)
            if not profile.is_admin:
                return HttpResponseForbidden("❌ You are not authorized to perform this action!")

            # 🔥 Completely delete the password protection entry
            org_protection.delete()  

            return JsonResponse({"success": True, "message": "✅ Password protection removed successfully!"})

        except Exception as e:
            return JsonResponse({"success": False, "message": f"❌ Error: {str(e)}"})

    return JsonResponse({"success": False, "message": "❌ Invalid request!"})


# FETCH ACCESS ACTIVITIES
@login_required
def fetch_activity_logs(request, org_id):
    """Fetch all access activities for a workspace with security enhancements"""
    
    organization = get_object_or_404(Organization, id=org_id)

    profile = get_object_or_404(Profile, organization=organization)

    if not profile.is_admin:
        return JsonResponse({'error:','You are not authorized to access the history!'},status=400)

    # Optimized query using select_related to minimize DB hits
    activities = TrackAccess.objects.filter(organization=organization).select_related("user").order_by("-accessed_at")

    # Serialize data
    activity_data = []
    for activity in activities:
        activity_data.append({
            "user": activity.user.get_full_name() or activity.user.username,
            "status": activity.access_type,  # SUCCESS, FAILED, TIMEOUT
            "device": activity.device_info or "Unknown Device",  
            "ip_address": activity.ip_address or "Unknown IP",
            "location": activity.location or "Unknown Location",
            "timestamp": localtime(activity.accessed_at).strftime("%b %d, %Y - %I:%M %p"),
            "failed_attempts": activity.failed_attempts,
        })

    return JsonResponse({"success": True, "activities": activity_data})



# CONFIGURE SETTINGS TO ADD PROTECTION
def get_protection_settings(request, org_id):
    """Fetch current protection settings for an organization."""
    org_protection = get_object_or_404(OrganizationProtection, organization_id=org_id)

    return JsonResponse({
        "protect_channels": org_protection.protect_channels,
        "protect_groups": org_protection.protect_groups,
        "protect_org_detail": org_protection.protect_org_detail,
        'protect_calendars':org_protection.protect_calendars,
        'protect_contacts':org_protection.protect_contacts,
        'protect_events':org_protection.protect_events,
        'protect_manage_members':org_protection.protect_manage_members,
    })


@csrf_exempt
def update_protection_settings(request, org_id):
    """Toggle protection settings via AJAX."""
    if request.method == "POST":
        data = json.loads(request.body)
        org_protection = get_object_or_404(OrganizationProtection, organization_id=org_id)

        # Update settings based on received data
        org_protection.protect_channels = data.get("protect_channels", org_protection.protect_channels)
        org_protection.protect_groups = data.get("protect_groups", org_protection.protect_groups)
        org_protection.protect_org_detail = data.get("protect_org_detail", org_protection.protect_org_detail)
        org_protection.protect_calendars = data.get("protect_calendars", org_protection.protect_calendars)
        org_protection.protect_contacts = data.get("protect_contacts", org_protection.protect_contacts)
        org_protection.protect_events = data.get("protect_events", org_protection.protect_events)
        org_protection.protect_manage_members = data.get("protect_manage_members", org_protection.protect_manage_members)

        org_protection.save()
        return JsonResponse({"success": True, "message": "Protection settings updated!"})

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)
