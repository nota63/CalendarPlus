from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.utils import timezone
from django.shortcuts import get_object_or_404,redirect
from django.core.mail import send_mail
from django.urls import reverse
from django.template.loader import render_to_string
import json
import secrets

from accounts.models import Organization, Profile, EmailInvitation
from django.conf import settings


@login_required
@require_POST
def create_organization_and_invite(request):
    try:
        data = json.loads(request.body)

        org_name = data.get('name')
        org_description = data.get('description', '')
        icon = request.FILES.get('icon')  # Optional
        status = data.get('status')

        if not org_name:
            return JsonResponse({'error': 'Organization name is required.'}, status=400)

        organization = Organization.objects.create(
            name=org_name,
            description=org_description,
            created_by=request.user,
            icon=icon,
            status=status
        )

        Profile.objects.create(
            user=request.user,
            organization=organization,
            is_admin=True
        )

        invitations = data.get('invitations', [])
        for invite in invitations:
            email = invite.get('email')
            role = invite.get('role')

            if role not in ['manager', 'employee'] or not email:
                continue

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
                'inviter_name': request.user.get_full_name() or request.user.username,
                'accept_invite_url': invite_url,
                'expiration_date': invitation.expires_at.strftime('%Y-%m-%d %H:%M'),
                'current_year': timezone.now().year,
            })

            send_mail(
                subject="You're Invited to Join an Organization",
                message=f"You've been invited to join {organization.name} as a {role}. Click to accept: {invite_url}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=html_content,
            )

        # Return redirect URL as part of JSON
        return JsonResponse({
            'success': True,
            'message': 'Organization created and invitations sent!',
            'redirect_url': reverse('org_detail', kwargs={'org_id': organization.id})
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
