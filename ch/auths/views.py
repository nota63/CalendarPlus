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
from .forms import InvitationForm, EmailInvitationForm , ProfileEditForm
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
        # Ensure the user is part of the organization
        organization = get_object_or_404(Organization, id=organization_id)
        user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
        
        # Check access permissions
        if not user_profile or not (user_profile.is_admin or user_profile.is_manager):
            return HttpResponseForbidden("You do not have permission to access this page.")

        # Fetch profiles based on role
        managers = Profile.objects.filter(organization=organization, is_manager=True)
        employees = Profile.objects.filter(organization=organization, is_employee=True)

        return render(request, 'auths/members_actions.html', {
            'organization': organization,
            'managers': managers,
            'employees': employees,
            'user_profile': user_profile,
        })

    def post(self, request, organization_id):
        organization = get_object_or_404(Organization, id=organization_id)
        user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
        
        if not user_profile or not (user_profile.is_admin or user_profile.is_manager):
            return HttpResponseForbidden("You do not have permission to perform this action.")

        # Fetch the profile to edit
        profile_id = request.POST.get('profile_id')
        new_role = request.POST.get('new_role')

        profile_to_edit = get_object_or_404(Profile, id=profile_id, organization=organization)
        
        # Role change logic based on permissions
        if user_profile.is_admin:
            if new_role == 'manager':
                profile_to_edit.is_manager = True
                profile_to_edit.is_employee = False
            elif new_role == 'employee':
                profile_to_edit.is_manager = False
                profile_to_edit.is_employee = True
            else:
                messages.error(request, "Invalid role provided.")
        elif user_profile.is_manager:
            if profile_to_edit.is_employee and new_role == 'employee':
                # Managers can only change employees to employees (if additional logic is needed)
                profile_to_edit.is_manager = False
                profile_to_edit.is_employee = True
            else:
                messages.error(request, "You can only edit employees.")
        
        profile_to_edit.save()
        messages.success(request, f"{profile_to_edit.user.username}'s role has been updated.")
        
        return redirect('members_action', organization_id=organization.id)
    

# remove employees from organization

class DeleteProfileView(View):
    def post(self, request, organization_id):

        organization = get_object_or_404(Organization, id=organization_id)
        user_profile = Profile.objects.filter(user=request.user, organization=organization).first()

        if not user_profile or not (user_profile.is_admin or user_profile.is_manager):
            return HttpResponseForbidden("You do not have permission to perform this action.")


        profile_id = request.POST.get('profile_id')
        profile_to_delete = get_object_or_404(Profile, id=profile_id, organization=organization)

 
        if profile_to_delete.user == request.user:
            messages.error(request, "You cannot delete yourself.")
            return redirect('members_action', organization_id=organization.id)

    
        if user_profile.is_admin:
            profile_to_delete.delete()
            messages.success(request, f"Deleted {profile_to_delete.user.username} from the organization.")

     
        elif user_profile.is_manager:
            if profile_to_delete.is_employee:
                profile_to_delete.delete()
                messages.success(request, f"Deleted {profile_to_delete.user.username} from the organization.")
            else:
                messages.error(request, "Managers can only delete employees.")

        return redirect('members_action', organization_id=organization.id)
    


#  CALENDAR PART 
# from .forms import AvailabilityForm
from .models import Availability
from datetime import datetime
from django.db import transaction
from django.contrib.auth.decorators import login_required

class CalendarRoomView(View):
    template_name = 'calendar+/calendar_room.html'

    def get(self, request):
        return render(request, self.template_name)


# set availability
class SetAvailabilityView(View):
    template_name = 'calendar+/set_availability.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in!')
            return redirect('set_availability')
    
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        days_of_week = request.POST.getlist('days_of_week[]')  
        start_times = request.POST.getlist('start_times[]')
        end_times = request.POST.getlist('end_times[]')
        meeting_duration = request.POST.get('meeting_duration')
        buffer_time = request.POST.get('buffer_time')
        is_recurring = request.POST.get('is_recurring') == 'on'

        if not days_of_week or not start_times or not end_times:
            messages.error(request, "Please fill in all required fields.")
            return render(request, self.template_name)

        errors = []

        
        for day, start, end in zip(days_of_week, start_times, end_times):
            if not day or not start or not end:
                errors.append("Missing day, start time, or end time.")
                continue


            if start >= end:
                errors.append(f"Start time must be earlier than end time for {day}.")
                continue

            
            try:
                self.create_multiple_slots(request, day, start, end, meeting_duration, buffer_time, is_recurring)
                
            except Exception as e:
                errors.append(f"Error saving availability for {day}: {e}")

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, self.template_name)

        messages.success(request, "Availability set successfully!")
        return redirect('set_availability')

    def create_multiple_slots(self, request, day, start, end, meeting_duration, buffer_time, is_recurring):
   
     try:
        start_time = datetime.strptime(start, "%H:%M").time()  
        end_time = datetime.strptime(end, "%H:%M").time()  
     except ValueError:
        raise ValueError("Invalid time format. Please ensure times are in HH:MM format.")

    # Combine date and time to create datetime objects
     start_datetime = datetime.combine(datetime.today(), start_time)
     end_datetime = datetime.combine(datetime.today(), end_time)

    # Convert meeting_duration and buffer_time to integers
     try:
        meeting_duration = int(meeting_duration)
        buffer_time = int(buffer_time)
     except ValueError:
        raise ValueError("Meeting duration and buffer time must be valid integers.")

    # Initialize the current time to start time
     current_time = start_datetime

    # Create slots while current_time is less than the end time
     while current_time + timedelta(minutes=meeting_duration) <= end_datetime:
        # Calculate the end time for the current slot (with buffer time added)
        slot_end_time = current_time + timedelta(minutes=meeting_duration)
        
        # Create an Availability object for the current slot
        Availability.objects.create(
            user=request.user,
            day_of_week=day,
            start_time=current_time.time(),
            end_time=slot_end_time.time(),
            meeting_duration=meeting_duration,
            buffer_time=buffer_time,
            is_recurring=is_recurring
        )
        
        # Move to the next slot by adding meeting duration and buffer time
        current_time = slot_end_time + timedelta(minutes=buffer_time)

# MANAGE AVAILABILITY

class ManageAvailabilityView(LoginRequiredMixin,TemplateView):
    template_name= 'calendar+/manage_availability.html'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['availabilities'] = Availability.objects.filter(user=self.request.user)
        context['days_of_week'] = [
            ("Monday", "Monday"),
            ("Tuesday", "Tuesday"),
            ("Wednesday", "Wednesday"),
            ("Thursday", "Thursday"),
            ("Friday", "Friday"),
            ("Saturday", "Saturday"),
            ("Sunday", "Sunday"),
        ]
        return context
    
    def post(self, request, *args , **kwargs):
        action = request.POST.get('action')

        if action == 'add':
            # add new availability

            days_of_week  = request.POST.getlist('days_of_week')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            meeting_duration = request.POST.get('meeting_duration')
            buffer_time = request.POST.get('buffer_time')
            is_recurring = request.POST.get('is_recurring') == 'on'

            for day in days_of_week:
                Availability.objects.create(
                    user=request.user,
                    day_of_week=day,
                    start_time=start_time,
                    end_time=end_time,
                    meeting_duration=meeting_duration,
                    buffer_time=buffer_time,
                    is_recurring=is_recurring
                )

            return JsonResponse({'message':'Availability added successfully'})

        elif action == 'edit':
            # edit the Availability 
            availability_id = request.POST.get('id')
            availability = get_object_or_404(Availability, id=availability_id, user = request.user)    

            availability.start_time = request.POST.get('start_time')
            availability.end_time = request.POST.get('end_time')
            availability.meeting_duration = request.POST.get('meeting_duration')
            availability.buffer_time = request.POST.get('buffer_time')
            availability.is_recurring = request.POST.get('is_recurring') == 'on'
            availability.save()
            return JsonResponse({'message': 'Availability updated successfully'})
        
        elif action == 'delete':
            # delete availability
            availability_id = request.POST.get('id')
            availability = get_object_or_404(Availability, id=availability_id, user=request.user)
            availability.delete()
            return JsonResponse({'message:':'Availability deleted successfully'})
        return JsonResponse({'error':'Invalid action'}, status = 400)
    

# set up the calendar 


from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from datetime import datetime, timedelta
from django.utils.dateparse import parse_datetime
from .models import Meets
from collections import defaultdict

# Class for rendering the calendar page


class CalendarView(LoginRequiredMixin, View):
    template_name = 'calendar+/calendar.html'

    def get(self, request):
        return render(request, self.template_name)
    
class AvailabilityCalendarView(View):
    def get(self, request, *args, **kwargs):
        user = request.user  # Assuming user is authenticated
        availabilities = Availability.objects.filter(user=user)

        day_mapping = {
            "Monday": 0,
            "Tuesday": 1,
            "Wednesday": 2,
            "Thursday": 3,
            "Friday": 4,
            "Saturday": 5,
            "Sunday": 6,
        }

        events = []
        today = datetime.today()

        for availability in availabilities:
            if availability.day_of_week:
                # Calculate the date for the next occurrence of the day_of_week
                current_day = today.weekday()
                target_day = day_mapping[availability.day_of_week]
                delta_days = (target_day - current_day) % 7
                availability_date = today + timedelta(days=delta_days)

                # Format start and end time as datetime strings
                start_datetime = datetime.combine(availability_date, availability.start_time)
                end_datetime = datetime.combine(availability_date, availability.end_time)

                # Add the event
                events.append({
                    "title": "Available",
                    "start": start_datetime.isoformat(),
                    "end": end_datetime.isoformat(),
                    "backgroundColor": "#28a745",  # Green for availability
                    "borderColor": "#28a745",
                    "isAvailability": True,  # Custom flag for availability
                })

        return JsonResponse(events, safe=False)
    





class GetUsersView(LoginRequiredMixin, View):
    def get(self, request):
        users = User.objects.all()
        user_list = [{'id': user.id, 'username': user.username} for user in users]
        return JsonResponse({'users': user_list})



# display all the users to view their calendar
class OrganizationMembersWithAvailabilityView(LoginRequiredMixin, View):
    template_name = 'calendar+/users_list.html'

    def get(self, request):
        # Fetch all users with valid availability
        users_with_valid_availability = User.objects.filter(
            availabilities__day_of_week__isnull=False,
            availabilities__start_time__isnull=False,
            availabilities__end_time__isnull=False
        ).distinct()

        # Fetch organizations for the logged-in user
        user_organizations = Organization.objects.filter(profiles__user=request.user)

        # Get members of user's organizations
        organization_members = {}
        for organization in user_organizations:
            members = Profile.objects.filter(
                organization=organization,
                user__in=users_with_valid_availability
            ).select_related('user')
            organization_members[organization] = members

        return render(request, self.template_name, {'organization_members': organization_members})







# get user calendar


class ViewUserCalendar(LoginRequiredMixin, View):
    template_name ='calendar+/user_calendar.html'

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        return render(request, self.template_name, {'user':user})
    


# fetch user availability
@login_required
def fetch_user_availability(request, user_id):
    availabilities = Availability.objects.filter(user_id=user_id)
    events = []
    
    # Map day_of_week to FullCalendar dow (0 = Sunday, 6 = Saturday)
    day_map = {
        "Sunday": 0,
        "Monday": 1,
        "Tuesday": 2,
        "Wednesday": 3,
        "Thursday": 4,
        "Friday": 5,
        "Saturday": 6,
    }

    for availability in availabilities:
        event_data = {
            "title": "Available",
            "color": "green" if availability.is_recurring else "blue",  # Green for recurring, blue for non-recurring
            "dayOfWeek": availability.day_of_week,
            "startTime": availability.start_time.strftime('%H:%M:%S'),
            "endTime": availability.end_time.strftime('%H:%M:%S'),
            "recurring": availability.is_recurring,
            "isBooked": availability.is_booked,  # Add the booking status here
        }

        if availability.is_recurring:
            # Recurring events (dow)
            event_data.update({
                "dow": [day_map[availability.day_of_week]],  # Day of week (0 = Sunday, 6 = Saturday)
            })
        else:
            # Non-recurring: specific start/end times on a particular day
            event_data.update({
                "start": f"{availability.day_of_week}T{availability.start_time.strftime('%H:%M:%S')}",
                "end": f"{availability.day_of_week}T{availability.end_time.strftime('%H:%M:%S')}",
            })
        events.append(event_data)
    
    return JsonResponse(events, safe=False)




@csrf_exempt
def schedule_meeting(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        title = request.POST.get('title')
        description = request.POST.get('description')
        day_of_week = request.POST.get('day_of_week')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        try:
            # Get the user
            user = User.objects.get(id=user_id)

            # Check if the availability slot exists and is not already booked
            availability = Availability.objects.filter(
                user=user,
                day_of_week=day_of_week,
                start_time=start_time,
                end_time=end_time,
                is_booked=False  # Ensure it's available
            ).first()

            if availability:
                # Create the meeting
                meeting = Meets.objects.create(
                    user=user,
                    title=title,
                    description=description,
                    day_of_week=day_of_week,
                    start_time=start_time,
                    end_time=end_time,
                    creator=request.user,  # Store the logged-in user as the creator
                )

                # Mark the availability slot as booked
                availability.is_booked = True
                availability.save()

                # Return the meeting details for updating the calendar
                return JsonResponse({
                    'success': True,
                    'start_time': start_time,
                    'end_time': end_time,
                    'event_id': f'{user_id}-{start_time}-{end_time}',
                })

            else:
                return JsonResponse({'success': False, 'error': 'Slot is already booked or does not exist.'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


    """END
    
    OF THE USER PART 
    

    EVERYTHING IS WORKING AS EXPECTED
    """

# MY CALENDAR VIEW 
@login_required
def user_calendar(request):
    return render(request,'calendar+/my_calendar.html')



@login_required
def fetch_user_meetings(request):
    user = request.user
    # Get meetings where the user is the creator or where the user is the participant
    meetings = Meets.objects.filter(user=user) | Meets.objects.filter(creator=user)

    events = []
    today = datetime.today()

    # Mapping days of the week to their corresponding weekday number
    weekday_mapping = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6,
    }

    for meeting in meetings:
        # Get the weekday number from the day_of_week field
        weekday_name = meeting.day_of_week.lower()  
        if weekday_name not in weekday_mapping:
            continue  # Skip if the weekday is invalid
        meeting_weekday = weekday_mapping[weekday_name]

        # Calculate the days ahead for the meeting
        days_ahead = (meeting_weekday - today.weekday()) % 7
        meeting_date = today + timedelta(days=days_ahead)
        
        # Combine the meeting date with start_time and end_time to create full datetime
        start_datetime = meeting_date.replace(hour=meeting.start_time.hour, minute=meeting.start_time.minute)
        end_datetime = meeting_date.replace(hour=meeting.end_time.hour, minute=meeting.end_time.minute)

        # Convert to ISO format (YYYY-MM-DDTHH:MM:SS)
        event_data = {
            'day_of_week':meeting.day_of_week,
            "title": meeting.title,
            "description": meeting.description,
            "start": start_datetime.isoformat(),
            "end": end_datetime.isoformat(),
            "user": meeting.user.username,  
            "creator": meeting.creator.username,  
            "color": "blue",  
        }
        events.append(event_data)

    return JsonResponse(events, safe=False)


# share my calendar
from django.conf import settings
from django.core.mail import send_mail
from .forms import ShareCalendarForm



class ShareCalendarView(View):
  def post(self, request, user_id):
    form = ShareCalendarForm(request.POST)
    if form.is_valid():
        email = form.cleaned_data['email']
        calendar_link = f"http://127.0.0.1:8000/features_auths/view-user-calendar/{user_id}/"

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({'message': 'User not found.'}, status=404)

        subject = f"Calendar Link - {user.username}"
        html_content = render_to_string(
            'calendar+/send_calendar.html',
            {
                'user': user,
                'calendar_link': calendar_link,
                'current_year': datetime.now().year
            }
        )
        message = f"Hello, you can view {user.username}'s calendar by following this link: {calendar_link}"
        from_email = settings.DEFAULT_FROM_EMAIL

        try:
            send_mail(subject, message, from_email, [email], html_message=html_content)
            return JsonResponse({'message': 'Calendar link sent successfully!'})
        except Exception as e:
            return JsonResponse({'message': f'Error sending email: {str(e)}'}, status=500)

    return JsonResponse({'message': 'Invalid email address.'}, status=400)
