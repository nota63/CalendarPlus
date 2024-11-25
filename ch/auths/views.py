from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from .models import Profile, Organization, Invitation, EmailInvitation
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView,  TemplateView
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseForbidden
from django.contrib.auth.models import User
from .forms import AddMemberForm
from django.core.exceptions import ValidationError
from datetime import timedelta
from .forms import InvitationForm, EmailInvitationForm
from django.views.generic.edit import FormView
from django.utils import timezone
from django.core.mail import send_mail
from django.urls import reverse


# Create your views here.
class FeaturesImplementation(View):
    template = 'auths/features_auths.html'

    def get(self, request):
        return render(request, self.template)
    




class CreateOrganizationView(LoginRequiredMixin,View):
    template = 'auths/create_organization.html'

    def get(self, request):
        return render(request, self.template)
    
    def post(self, request):
        name = request.POST.get('name')
        description = request.POST.get('description')

        try:
            # create the organization

            organization = Organization.objects.create(
                name = name, 
                description = description,
                created_by = request.user
            )

            # assign the creator as admin
            Profile.objects.create(
                user = request.user ,
                organization = organization ,
                is_admin = True
            )

            messages.success(request,'organization created successfully')
            return redirect('create_organization')
        except Exception as e:
            return JsonResponse({'exception':str(e)}, status = 500)

            
# ADD MEMBERS 

# organizations


class OrganizationListView(LoginRequiredMixin, ListView):
    model = Organization
    template_name = 'auths/organizations_list.html'
    context_object_name = 'organizations'

    def get_queryset(self):
     
        user_profiles = Profile.objects.filter(user=self.request.user)
        return Organization.objects.filter(profiles__in=user_profiles)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['user_profiles'] = Profile.objects.filter(user=self.request.user)
        return context
    

class OrganizationEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Organization
    fields = ['name', 'description']
    template_name = 'auths/organization_edit.html'
    context_object_name = 'organization'

    def test_func(self):
      
        organization = self.get_object()
        user_profile = Profile.objects.filter(user=self.request.user, organization=organization).first()
        return user_profile and (user_profile.is_admin or user_profile.is_manager)

    def form_valid(self, form):
        
        form.save()
        return redirect('organization_list')  
    
# add members 
class AddMemberView(LoginRequiredMixin, View):
    def get(self, request, organization_id):
        organization = get_object_or_404(Organization, id=organization_id)

        # Ensure the user has permission to add members (Admin or Manager)
        user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
        if not user_profile or not (user_profile.is_admin or user_profile.is_manager):
            return HttpResponseForbidden("You do not have permission to add members.")

        # Instantiate the form with the organization as context
        form = AddMemberForm(organization=organization)

        return render(request, 'auths/add_member.html', {
            'organization': organization,
            'form': form
        })

    def post(self, request, organization_id):
        organization = get_object_or_404(Organization, id=organization_id)

        # Ensure the user has permission to add members (Admin or Manager)
        user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
        if not user_profile or not (user_profile.is_admin or user_profile.is_manager):
            return HttpResponseForbidden("You do not have permission to add members.")

        # Instantiate the form with POST data and organization context
        form = AddMemberForm(request.POST, organization=organization)

        if form.is_valid():
            # Save the new profile for the user in the organization
            user = form.cleaned_data['user']
            role = form.cleaned_data['role']

            # Check if the user is already a member of the organization
            if Profile.objects.filter(user=user, organization=organization).exists():
                form.add_error('user', 'This user is already a member of the organization.')
                return render(request, 'auths/add_member.html', {
                    'organization': organization,
                    'form': form
                })

            # Initialize the role flags
            is_admin = False
            is_manager = False
            is_employee = False

            # Ensure that only one admin exists
            if role == 'manager' and user_profile.is_admin:
                # For manager, set is_manager to True and other flags to False
                is_manager = True
            elif role == 'employee':
                # For employee, set is_employee to True and other flags to False
                is_employee = True
            elif role == 'admin':
                # Ensure only one admin in the organization
                if Profile.objects.filter(organization=organization, is_admin=True).exists():
                    form.add_error('role', 'An organization can have only one admin.')
                    return render(request, 'auths/add_member.html', {
                        'organization': organization,
                        'form': form
                    })
                # For admin, set is_admin to True and other flags to False
                is_admin = True
            else:
                # If role is invalid, do not proceed
                form.add_error('role', 'Invalid role selection.')
                return render(request, 'auths/add_member.html', {
                    'organization': organization,
                    'form': form
                })

            # Create the Profile for the user
            Profile.objects.create(
                user=user,
                organization=organization,
                is_admin=is_admin,
                is_manager=is_manager,
                is_employee=is_employee
            )

            return redirect('organization_list')  # Redirect to the organization list

        return render(request, 'auths/add_member.html', {
            'organization': organization,
            'form': form
        })

# all org members     
class OrganizationMembersView(View):
    def get(self, request, organization_id):
        # Get the organization by its ID
        organization = get_object_or_404(Organization, id=organization_id)

        # Filter profiles based on the organization and role
        admins = Profile.objects.filter(organization=organization, is_admin=True)
        managers = Profile.objects.filter(organization=organization, is_manager=True)
        employees = Profile.objects.filter(organization=organization, is_employee=True)

        return render(request, 'auths/organization_members.html', {
            'organization': organization,
            'admins': admins,
            'managers': managers,
            'employees': employees
        })   


# invitation functionality 
class InviteMemberView(LoginRequiredMixin, View):
    def get(self, request, organization_id):
        # Fetch the organization using the ID
        organization = get_object_or_404(Organization, id=organization_id)

        # Ensure the user has permission to send invitations (Admin or Manager)
        user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
        if not user_profile or not (user_profile.is_admin or user_profile.is_manager):
            return HttpResponseForbidden("You do not have permission to invite members.")

        # Pass the user and preselect the organization in the form
        form = InvitationForm(user=request.user, initial={'organization': organization})

        return render(request, 'auths/send_invitations.html', {
            'organization': organization,
            'form': form
        })

    def post(self, request, organization_id):
        # Fetch the organization using the ID
        organization = get_object_or_404(Organization, id=organization_id)

        # Ensure the user has permission to send invitations (Admin or Manager)
        user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
        if not user_profile or not (user_profile.is_admin or user_profile.is_manager):
            return HttpResponseForbidden("You do not have permission to invite members.")

        # Pass the user to the form
        form = InvitationForm(request.POST, user=request.user)

        if form.is_valid():
            # Fetch invitee and role from the form data
            invitee = form.cleaned_data['invitee']
            role = form.cleaned_data['role']

            # Create the invitation
            Invitation.objects.create(
                inviter=request.user,
                invitee=invitee,
                organization=organization,
                role=role,
                expires_at=timezone.now() + timezone.timedelta(days=7)
            )
            messages.success(request, f"Invitation sent to {invitee.username} as {role}.")
            return redirect('organization_list')

        return render(request, 'auths/send_invitations.html', {
            'organization': organization,
            'form': form
        })


# accept the invitation
class AcceptInvitationView(View):
    def get(self, request, *args, **kwargs):
    
        invitation = get_object_or_404(Invitation, id=kwargs['invitation_id'])

   
        if not invitation.is_valid():
            return HttpResponseForbidden("This invitation is no longer valid.")

        if invitation.accept_invitation():
            messages.info('you are now a part of the organization')

            return redirect('organization_list')
        return HttpResponseForbidden("You cannot accept this invitation.")


# view invitations

class ViewInvitationsView(ListView):
    model = Invitation
    template_name = 'auths/view_invitations.html'
    context_object_name = 'invitations'

    def get_queryset(self):
        # Only show invitations for the current user and that are still pending
        return Invitation.objects.filter(invitee=self.request.user, status='pending')

    def post(self, request, *args, **kwargs):
        invitation_id = request.POST.get('invitation_id')
        action = request.POST.get('action')

        # Get the invitation
        invitation = Invitation.objects.filter(id=invitation_id).first()

        if not invitation or invitation.invitee != request.user:
            return HttpResponseForbidden("You do not have permission to act on this invitation.")

        if action == 'accept':
            invitation.accept_invitation()
            return redirect('view_invitations')
        elif action == 'reject':
            invitation.reject_invitation()
            return redirect('view_invitations')

        return HttpResponseForbidden("Invalid action.")

# EMAIL INVITATION
from django.conf import settings
from django.template.loader import render_to_string

class SendEmailInvitationView(LoginRequiredMixin, View):
    def get(self, request, organization_id):
        organization = get_object_or_404(Organization, id=organization_id)

        # Ensure the user has permission to send invitations (Admin or Manager)
        user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
        if not user_profile or not (user_profile.is_admin or user_profile.is_manager):
            return HttpResponseForbidden("You do not have permission to invite members.")

        form = EmailInvitationForm()
        return render(request, 'auths/send_email_invitation.html', {
            'organization': organization,
            'form': form
        })

    def post(self, request, organization_id):
        organization = get_object_or_404(Organization, id=organization_id)

        # Ensure the user has permission to send invitations (Admin or Manager)
        user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
        if not user_profile or not (user_profile.is_admin or user_profile.is_manager):
            return HttpResponseForbidden("You do not have permission to invite members.")

        form = EmailInvitationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            role = form.cleaned_data['role']

            # Create the email invitation
            invitation = EmailInvitation.objects.create(
                inviter=request.user,
                invitee_email=email,
                organization=organization,
                role=role,
                expires_at=timezone.now() + timezone.timedelta(days=7)  # 7 days validity
            )

            # Send the email
            invite_url = request.build_absolute_uri(
                reverse('accept_email_invitation', kwargs={'token': invitation.token})
            )

            html_content = render_to_string('auths/invitation_template.html', {
              'organization_name': organization.name,
              'role': role,
              'inviter_name':invitation.inviter.get_full_name() or invitation.inviter.username,
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

            messages.success(request, f"Invitation sent to {email}.")
            return redirect('organization_list')

        return render(request, 'auths/send_email_invitation.html', {
            'organization': organization,
            'form': form
        })



class AcceptEmailInvitationView(View):
    def get(self, request, token):
        invitation = get_object_or_404(EmailInvitation, token=token)

        if not invitation.is_valid():
            return HttpResponseForbidden("This invitation has expired or is invalid.")

        return render(request, 'auths/accept_email_invitation.html', {'invitation': invitation})

    def post(self, request, token):
        invitation = get_object_or_404(EmailInvitation, token=token)

        if not invitation.is_valid():
            return HttpResponseForbidden("This invitation has expired or is invalid.")

        # Check if the invitee already has an account
        if not request.user.is_authenticated:
            return redirect('login')  # Redirect to login if user is not logged in

        # Accept the invitation
        invitation.accept_invitation(user=request.user)
        messages.success(request, f"You have successfully joined {invitation.organization.name} as a {invitation.role}.")
        return redirect('organization_list')


class RejectEmailInvitationView(View):
    def post(self, request, token):
        invitation = get_object_or_404(EmailInvitation, token=token)

        if not invitation.is_valid():
            return HttpResponseForbidden("This invitation has expired or is invalid.")

        # Reject the invitation
        invitation.reject_invitation()
        messages.success(request, "You have successfully rejected the invitation.")
        return redirect('organization_list')


# invitation status

class InvitationStatusView(LoginRequiredMixin, ListView):
    template_name = 'auths/invitation_status.html'
    context_object_name = 'invitations'

    def get_queryset(self):
        # Get the organization by ID
        organization_id = self.kwargs.get('organization_id')
        organization = get_object_or_404(Organization, id=organization_id)

        # Check if the user is an admin or manager of the organization
        user_profile = Profile.objects.filter(user=self.request.user, organization=organization).first()
        if not user_profile or not (user_profile.is_admin or user_profile.is_manager):
            return HttpResponseForbidden("You do not have permission to view this page.")

        # Fetch normal and email invitations for the organization
        normal_invitations = Invitation.objects.filter(organization=organization)
        email_invitations = EmailInvitation.objects.filter(organization=organization)

        return {
            'normal_invitations': normal_invitations,
            'email_invitations': email_invitations,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_queryset())  # Add both types of invitations to the context
        return context
    

# actions on org members
class ActionMembersView(View):
    def get(self, request, organization_id):
     
        organization = get_object_or_404(Organization, id=organization_id)


        user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
        if not user_profile or not (user_profile.is_admin or user_profile.is_manager):
            return HttpResponseForbidden("You do not have permission to view or manage members of this organization.")

        admins = Profile.objects.filter(organization=organization, is_admin=True)
        managers = Profile.objects.filter(organization=organization, is_manager=True)
        employees = Profile.objects.filter(organization=organization, is_employee=True)

        return render(request, 'auths/members_actions.html', {
            'organization': organization,
            'admins': admins,
            'managers': managers,
            'employees': employees,
            'user_profile': user_profile
        })

    def post(self, request, organization_id):
        # Get the organization by its ID
        organization = get_object_or_404(Organization, id=organization_id)

        # Ensure the user is an admin or manager in the organization
        user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
        if not user_profile or not (user_profile.is_admin or user_profile.is_manager):
            return HttpResponseForbidden("You do not have permission to manage members of this organization.")
        
        profile_id = request.POST.get('profile_id')
        profile_to_delete = get_object_or_404(Profile, id=profile_id)


        if profile_to_delete.user == request.user:
            messages.error(request, "You cannot delete yourself.")
            return redirect('organization_members', organization_id=organization.id)
        
        if user_profile.is_admin:
            if profile_to_delete.is_admin or profile_to_delete.is_manager:
                profile_to_delete.delete()
                messages.success(request, f"Deleted {profile_to_delete.user.username} from the organization.")
            else:
                messages.error(request, "Admins cannot delete other admins or managers.")

        elif user_profile.is_manager:
            if profile_to_delete.is_employee:
                profile_to_delete.delete()
                messages.success(request, f"Deleted {profile_to_delete.user.username} from the organization.")
            else:
                messages.error(request, "Managers can only delete employees.")
        
        return redirect('members_action', organization_id=organization.id)