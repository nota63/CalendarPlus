from django.shortcuts import render, redirect, get_object_or_404
from accounts.models import Organization, Profile, EmailInvitation
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.http import JsonResponse
from django.db.models import Q, Case, When, Value, CharField 
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils import timezone
import secrets
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.decorators import login_required


# display the members

def manage_members(request, org_id):
    organization = get_object_or_404(Organization, id=org_id)
   
    user_profile=Profile.objects.filter(organization=organization,user=request.user).first()
    print("PROFILE FETCHED:",user_profile)
  
    
  
    query = request.GET.get('q', '')
    members = Profile.objects.filter(
        organization=organization
    ).exclude(user=request.user)

    if query:
        members = members.filter(
            Q(user__username__icontains=query) | Q(user__email__icontains=query)
        )

   
    members = members.annotate(
        role=Case(
            When(is_admin=True, then=Value("Admin")),
            When(is_manager=True, then=Value("Manager")),
            default=Value("Employee"),
            output_field=CharField(),
        )
    )
    

    

    

    context = {
        "organization": organization,
        "members": members,
        "query": query,
        'user_profile':user_profile,
    
    }
    return render(request, "profiles/manage_members/manage_members.html", context)


# Change role

@csrf_exempt
def change_role(request, org_id, member_id):
    if request.method == "POST":
        try:
           
            data = json.loads(request.body)

           
            organization = get_object_or_404(Organization, id=org_id)
            member_profile = get_object_or_404(Profile, id=member_id, organization=organization)
            current_user_profile = Profile.objects.get(user=request.user, organization=organization)

         
            if not current_user_profile.is_admin and not current_user_profile.is_manager:
                return JsonResponse({"error": "You don't have permission to change roles."}, status=403)
            
            if current_user_profile.is_manager and member_profile.is_manager:
                return JsonResponse({"error": "Managers cannot change roles of other managers."}, status=403)

        
            new_role = data.get("new_role")
            if new_role not in ["manager", "employee"]:
                return JsonResponse({"error": "Invalid role provided."}, status=400)

          
            if new_role == "manager":
                member_profile.is_manager = True
                member_profile.is_employee = False
            elif new_role == "employee":
                member_profile.is_manager = False
                member_profile.is_employee = True

            member_profile.save()
            return JsonResponse({"success": f"Role updated to {new_role}."})

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)
    
    return JsonResponse({"error": "Invalid request method."}, status=405)



# Remove member from organization

@csrf_exempt
def remove_member(request, org_id, member_id):
    if request.method == "POST":
        
        organization = get_object_or_404(Organization, id=org_id)
        member_profile = get_object_or_404(Profile, id=member_id, organization=organization)
        current_user_profile = Profile.objects.get(user=request.user, organization=organization)

    
        if not current_user_profile.is_admin and not current_user_profile.is_manager:
            return JsonResponse({"error": "You don't have permission to remove members."}, status=403)
        
        if current_user_profile.is_manager and member_profile.is_manager:
            return JsonResponse({"error": "Managers cannot remove other managers."}, status=403)
        
       
        member_profile.delete()

        return JsonResponse({"success": "Member removed from the organization."})

    return JsonResponse({"error": "Invalid request method."}, status=405)


# Send Email Invitation
@csrf_exempt
def send_email_invitation(request, org_id):
    if request.method == 'POST':
        try:
          
            data = json.loads(request.body.decode('utf-8'))
            email = data.get('email')
            role = data.get('role')

         
            if not email or role not in ['manager', 'employee']:
                return JsonResponse({"error": "Invalid email or role."}, status=400)

            organization = get_object_or_404(Organization, id=org_id)

           
            user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
            if not user_profile or not (user_profile.is_admin or user_profile.is_manager):
                return JsonResponse({"error": "You do not have permission to invite members."}, status=403)

       
            invitation = EmailInvitation.objects.create(
                inviter=request.user,
                invitee_email=email,
                organization=organization,
                role=role,
                expires_at=timezone.now() + timezone.timedelta(days=7)  
            )

       
            invite_url = request.build_absolute_uri(
                reverse('accept_email_invitation', kwargs={'token': invitation.token})
            )

            html_content = render_to_string('calendar/invitation_template.html', {
                'organization_name': organization.name,
                'role': role,
                'inviter_name': invitation.inviter.get_full_name() or invitation.inviter.username,
                'accept_invite_url': invite_url,
                'expiration_date': invitation.expires_at.strftime('%Y-%m-%d %H:%M'),
                'current_year': timezone.now().year,
            })
            send_mail(
                subject="You're Invited to Join an Organization",
                message=f"You've been invited to join {organization.name} as a {role}. "
                        f"Click the link to accept: {invite_url}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                html_message=html_content,
                recipient_list=[email],
            )

            return JsonResponse({"success": f"Invitation sent to {email}."})

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=405)




# DISPLAY INVITATION STATUS
@csrf_exempt
def fetch_invitations_status(request, org_id):
    organization = get_object_or_404(Organization, id=org_id)

    
    invitations = EmailInvitation.objects.filter(organization=organization)


    invitation_data = []

    for invitation in invitations:
        invitation_data.append({
            'invitee_email': invitation.invitee_email,
            'role': invitation.get_role_display(),
            'status': invitation.get_status_display(),
            'inviter': invitation.inviter.get_full_name() or invitation.inviter.username,
            'expires_at': invitation.expires_at.strftime('%Y-%m-%d %H:%M:%S'),
            'is_valid': invitation.is_valid(),
        })

    return JsonResponse({'invitations': invitation_data})


