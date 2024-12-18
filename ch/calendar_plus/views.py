from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from accounts.models import Profile, Organization,  EmailInvitation
from meet.models import MeetInvitation
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
from .forms import EmailInvitationForm , ProfileEditForm
from django.views.generic.edit import FormView
from django.utils import timezone
from django.core.mail import send_mail
from django.urls import reverse
from django.db.models import Count , Avg, F, Sum
from django.db.models import Count, Avg, Sum, ExpressionWrapper, F, DurationField, When,  Case, When, Value
from datetime import timedelta
from django.utils.timezone import make_aware
import json
from django.db.models.functions import TruncMonth, TruncHour
from django.db.models import Count, Q
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import now
from datetime import date, datetime
from django.utils.dateparse import parse_date
from meet.models import Contacts, FavoriteContact
from django.conf import settings
from django.template.loader import render_to_string
from accounts.models import Availability
from datetime import datetime
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail
from .forms import ShareCalendarForm, ReminderForm
from meet.models import Reminder
from django.views.generic import DetailView, FormView
from django.http import HttpResponse
from meet.models import MeetInvitation
from formtools.wizard.views import SessionWizardView
from .forms import OrganizationNameForm, OrganizationDescriptionForm, ProfileInfoForm, CurrentProjectForm
from django.core.files.storage import FileSystemStorage
import os
from django.views.generic.edit import FormView
from .forms import EventForm, EventTypeForm, BookingForm, EventEditForm
from django.urls import reverse_lazy, reverse
from.models import Event
from django.utils.timezone import now
from datetime import datetime, timedelta
from .models import Booking
import json
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from accounts.models import Project
from django.http import HttpResponseRedirect
from .forms import ProjectForm, AssignEmployeeForm, AssignManagerForm
from accounts.models import ProjectEmployeeAssignment,ProjectManagerAssignment
from django.shortcuts import render, get_object_or_404, redirect
from accounts.models import Organization, Project, Profile, ProjectManagerAssignment
from .forms import AssignManagerForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from datetime import datetime, timedelta
from django.utils.dateparse import parse_datetime
from meet.models import Meets
from collections import defaultdict
from django.utils.timezone import localdate
from django.utils.timezone import make_aware
from datetime import timedelta
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

# Create your views here.
class FeaturesImplementation(View):
    template = 'calendar/features_calendar.html'

    def get(self, request):
        return render(request, self.template)
    

# landing page 

class LandingPageView(LoginRequiredMixin, TemplateView):
    """
    Landing page view to check if a user belongs to any organization.
    Redirects to the organization list if the user is a member of any organization.
    Otherwise, shows an option to create an organization.
    """
    template_name = "landing_page/landing_page.html"
    login_url = '/login/' 

    def get(self, request, *args, **kwargs):
        try:
      
            if not request.user.is_authenticated:
                return redirect(self.login_url)

           
            user_profiles = Profile.objects.filter(user=request.user)

            if user_profiles.exists():
            
                return redirect('organization_list')

           
            return super().get(request, *args, **kwargs)

        except Exception as e:
        
            print(f"Error in LandingPageView: {e}")

        
            return JsonResponse({'exception':str(e)}, status = 400)

# create organization

TEMP_FILE_STORAGE = FileSystemStorage(location=os.path.join("media", "temp"))

FORMS = [
    ("org_name", OrganizationNameForm),
    ("org_desc", OrganizationDescriptionForm),
    ("profile_info", ProfileInfoForm),
    ("current_project", CurrentProjectForm),
]

TEMPLATES = {
    "org_name": "wizard/organization_name.html",
    "org_desc": "wizard/organization_description.html",
    "profile_info": "wizard/profile_info.html",
    "current_project": "wizard/current_project.html",
}

class CreateOrganizationWizardView(SessionWizardView):
    form_list = FORMS
    file_storage = TEMP_FILE_STORAGE

    def get_template_names(self):
        """Select the template based on the current step."""
        return [TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):
        """Handle the form submission at the end."""
   
        data = {key: form.cleaned_data for key, form in zip(self.get_form_list(), form_list)}

        try:
     
            organization = Organization.objects.create(
                name=data["org_name"]["name"],
                description=data["org_desc"]["description"],
                created_by=self.request.user,
            )

         
            if not hasattr(self.request.user, 'profile'):
                profile = Profile.objects.create(
                    user=self.request.user,
                    organization=organization,
                    full_name=data["profile_info"]["full_name"],
                    profile_picture=data["profile_info"].get("profile_picture"),
                    is_admin=True,
                )
            else:
                profile = self.request.user.profile
                profile.organization = organization
                profile.full_name = data["profile_info"]["full_name"]
                profile.profile_picture = data["profile_info"].get("profile_picture")
                profile.save()

       
            project_name = data["current_project"].get("current_project")
            if not project_name:
                messages.error(self.request, "Project name is missing.")
                return redirect("create_organization")

      
            project = Project.objects.create(
                name=project_name,
                description="null",
                organization=organization,
                created_by=profile,  
            )

    
            messages.success(self.request, "Organization and Project created successfully!")

            return redirect("org_detail", org_id=organization.id)

        except Exception as e:
       
            messages.error(self.request, f"Error creating organization or project: {e}")
            return redirect("create_organization")
        


# edit profile 
class EditProfileView(LoginRequiredMixin, View):
    template = 'calendar/view_edit_profile.html'

    def get(self, request, org_id):
        
        organization = Organization.objects.get(id=org_id)
        
      
        profile = Profile.objects.get(user=request.user, organization=organization)

        context = {
            'organization': organization,
            'profile': profile,
            'hide_checkbox': True,  
        }
        return render(request, self.template, context)

    def post(self, request, org_id):
      
        organization = Organization.objects.get(id=org_id)
        
       
        profile = Profile.objects.get(user=request.user, organization=organization)

     
        full_name = request.POST.get('full_name')
        profile_picture = request.FILES.get('profile_picture')

        profile.full_name = full_name
        if profile_picture:
            profile.profile_picture = profile_picture

        profile.save()

        messages.success(request, "Profile updated successfully!")
        return redirect('view_edit_profile',org_id=organization.id)



# ADD MEMBERS 

# organizations


class OrganizationListView(LoginRequiredMixin, ListView):
    model = Organization
    template_name = 'calendar/organizations_list.html'
    context_object_name = 'organizations'

    def get_queryset(self):
     
        user_profiles = Profile.objects.filter(user=self.request.user)
        return Organization.objects.filter(profiles__in=user_profiles)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['user_profiles'] = Profile.objects.filter(user=self.request.user)
        return context
    
# org detail
class OrgDetailView(LoginRequiredMixin, View):
    template_name = 'calendar/org_detail.html'

    def get(self, request, org_id):
        # Get the organization
        organization = get_object_or_404(Organization, id=org_id)

        
        user_profiles = Profile.objects.filter(organization=organization, user=request.user)

     
        is_admin = user_profiles.filter(is_admin=True).exists()
        is_manager = user_profiles.filter(is_manager=True).exists()
        is_employee = user_profiles.filter(is_employee=True).exists()

        
        context = {
            'organization': organization,
            'user_profiles': user_profiles,
            'is_admin': is_admin,
            'is_manager': is_manager,
            'is_employee': is_employee,
        }
        return render(request, self.template_name, context)
    



class OrganizationEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Organization
    fields = ['name', 'description','current_project']
    template_name = 'calendar/organization_edit.html'
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

        return render(request, 'calendar/add_member.html', {
            'organization': organization,
            'form': form
        })

    def post(self, request, organization_id):
        organization = get_object_or_404(Organization, id=organization_id)

    
        user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
        if not user_profile or not (user_profile.is_admin or user_profile.is_manager):
            return HttpResponseForbidden("You do not have permission to add members.")

   
        form = AddMemberForm(request.POST, organization=organization)

        if form.is_valid():
            user = form.cleaned_data['user']
            role = form.cleaned_data['role']

          
            if Profile.objects.filter(user=user, organization=organization).exists():
                form.add_error('user', 'This user is already a member of the organization.')
                return render(request, 'calendar/add_member.html', {
                    'organization': organization,
                    'form': form
                })

  
            is_admin = False
            is_manager = False
            is_employee = False

            
            if role == 'manager' and user_profile.is_admin:
              
                is_manager = True
            elif role == 'employee':
               
                is_employee = True
            elif role == 'admin':
                
                if Profile.objects.filter(organization=organization, is_admin=True).exists():
                    form.add_error('role', 'An organization can have only one admin.')
                    return render(request, 'calendar/add_member.html', {
                        'organization': organization,
                        'form': form
                    })
                
                is_admin = True
            else:
                
                form.add_error('role', 'Invalid role selection.')
                return render(request, 'calendar/add_member.html', {
                    'organization': organization,
                    'form': form
                })

       
            Profile.objects.create(
                user=user,
                organization=organization,
                is_admin=is_admin,
                is_manager=is_manager,
                is_employee=is_employee
            )

            return redirect('organization_list')  

        return render(request, 'calendar/add_member.html', {
            'organization': organization,
            'form': form
        })




# accept the invitation
class AcceptInvitationView(LoginRequiredMixin,View):
      pass

# view invitations

class ViewInvitationsView(LoginRequiredMixin,ListView):
    pass

# EMAIL INVITATION


class SendEmailInvitationView(LoginRequiredMixin, View):
    def get(self, request, organization_id):
        organization = get_object_or_404(Organization, id=organization_id)

        # Ensure the user has permission to send invitations (Admin or Manager)
        user_profile = Profile.objects.filter(user=request.user, organization=organization).first()
        if not user_profile or not (user_profile.is_admin or user_profile.is_manager):
            return HttpResponseForbidden("You do not have permission to invite members.")

        form = EmailInvitationForm()
        return render(request, 'calendar/send_email_invitation.html', {
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

            html_content = render_to_string('calendar/invitation_template.html', {
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

        return render(request, 'calendar/send_email_invitation.html', {
            'organization': organization,
            'form': form
        })



class AcceptEmailInvitationView(LoginRequiredMixin,View):
    def get(self, request, token):
        if not request.user.is_authenticated:
            return redirect('login')  
        
        invitation = get_object_or_404(EmailInvitation, token=token)

        if not invitation.is_valid():
            return HttpResponseForbidden("This invitation has expired or is invalid.")

        return render(request, 'calendar/accept_email_invitation.html', {'invitation': invitation})

    def post(self, request, token):
        invitation = get_object_or_404(EmailInvitation, token=token)

        if not invitation.is_valid():
            return HttpResponseForbidden("This invitation has expired or is invalid.")

       
        if not request.user.is_authenticated:
            return redirect('login')  
   
        invitation.accept_invitation(user=request.user)
        messages.success(request, f"You have successfully joined {invitation.organization.name} as a {invitation.role}.")
        return redirect('organization_list')
    



class RejectEmailInvitationView(LoginRequiredMixin,View):
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
    template_name = 'calendar/invitation_status.html'
    context_object_name = 'invitations'

    def get_queryset(self):

        organization_id = self.kwargs.get('organization_id')
        organization = get_object_or_404(Organization, id=organization_id)

        # Check if the user is an admin or manager of the organization
        user_profile = Profile.objects.filter(user=self.request.user, organization=organization).first()
        if not user_profile or not (user_profile.is_admin or user_profile.is_manager):
            return HttpResponseForbidden("You do not have permission to view this page.")

        email_invitations = EmailInvitation.objects.filter(organization=organization)

        return {
           
            'email_invitations': email_invitations,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_queryset())  
        return context
    

class ActionMembersView(View):
    def get(self, request, organization_id):
       
        organization = get_object_or_404(Organization, id=organization_id)
        user_profile = Profile.objects.filter(user=request.user, organization=organization).first()


           
        admins_all = Profile.objects.filter(organization=organization, is_admin=True)
        managers_all = Profile.objects.filter(organization=organization, is_manager=True)
        employee_all = Profile.objects.filter(organization=organization, is_employee=True)


        if not user_profile or not (user_profile.is_admin or user_profile.is_manager):
            return HttpResponseForbidden("You do not have permission to access this page.")

        managers = Profile.objects.filter(organization=organization, is_manager=True)
        employees = Profile.objects.filter(organization=organization, is_employee=True)

        return render(request, 'calendar/members_actions.html', {
            'organization': organization,
            'managers': managers,
            'employees': employees,
            'user_profile': user_profile,

            'admins_all':admins_all,
            'managers_all':managers_all,
            'employee_all':employee_all
        })




    def post(self, request, organization_id):
        organization = get_object_or_404(Organization, id=organization_id)
        user_profile = Profile.objects.filter(user=request.user, organization=organization).first()


      
        if not user_profile or not (user_profile.is_admin or user_profile.is_manager):
            return HttpResponseForbidden("You do not have permission to perform this action.")

      
        profile_id = request.POST.get('profile_id')
        new_role = request.POST.get('new_role')
        action = request.POST.get('action') 

        profile_to_edit = get_object_or_404(Profile, id=profile_id, organization=organization)

        if action == 'update': 
            if user_profile.is_admin:
                if new_role == 'manager':
                    profile_to_edit.is_manager = True
                    profile_to_edit.is_employee = False
                elif new_role == 'employee':
                    profile_to_edit.is_manager = False
                    profile_to_edit.is_employee = True
                else:
                    messages.error(request, "Invalid role provided.")
            elif user_profile.is_manager and profile_to_edit.is_employee and new_role == 'employee':
                profile_to_edit.is_manager = False
                profile_to_edit.is_employee = True
            else:
                messages.error(request, "You can only edit employees.")
            profile_to_edit.save()
            messages.success(request, f"{profile_to_edit.user.username}'s role has been updated.")

        elif action == 'remove':  
            profile_to_edit.organization = None
            profile_to_edit.is_manager = False
            profile_to_edit.is_employee = False
            profile_to_edit.save()
            messages.success(request, f"{profile_to_edit.user.username} has been removed from the organization.")

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





# PROJECT PART 


# create the project
class CreateProjectView(View):
    def get(self, request, org_id):
        """Render the project creation form."""
        try:
            # Fetch the organization by its ID
            organization = Organization.objects.get(id=org_id)
            
            # Check if the current user is an admin of the organization
            if not Profile.objects.filter(user=request.user, organization=organization, is_admin=True).exists():
                messages.error(request, "You do not have permission to create a project in this organization.")
                return redirect('org_detail', org_id=organization.id)
            
            # Initialize the project form
            form = ProjectForm()
            return render(request, 'project/create_project.html', {'form': form, 'organization': organization})

        except Organization.DoesNotExist:
            messages.error(request, "Organization not found.")
            return redirect('home')

    def post(self, request, org_id):
        """Handle the form submission for creating a project."""
        try:
            organization = Organization.objects.get(id=org_id)
            
            if not Profile.objects.filter(user=request.user, organization=organization, is_admin=True).exists():
                messages.error(request, "You do not have permission to create a project in this organization.")
                return redirect('org_detail', org_id=organization.id)
            
        
            form = ProjectForm(request.POST)
            if form.is_valid():
               
                project = form.save(commit=False)
                project.organization = organization
                
                
                profile = Profile.objects.get(user=request.user, organization=organization)
                project.created_by = profile  
                
                project.save()
                
                
                messages.success(request, "Project created successfully!")
                return redirect('org_detail', org_id=organization.id)
            else:
                return render(request, 'project/create_project.html', {'form': form, 'organization': organization})

        except Organization.DoesNotExist:
            messages.error(request, "Organization not found.")
            return redirect('home')


# project actions
class ProjectListView(View):
    def get(self, request, org_id):
        """Display the projects of the logged-in organization admin."""
        try:
   
            organization = Organization.objects.get(id=org_id)

   
            profile = Profile.objects.filter(user=request.user, organization=organization, is_admin=True).first()
            if not profile:
                messages.error(request, "You do not have permission to view projects in this organization.")
                return redirect('org_detail', org_id=organization.id)

            
            projects = Project.objects.filter(organization=organization)

           
            return render(request, 'project/project_list.html', {
                'organization': organization,
                'projects': projects
            })
        except Organization.DoesNotExist:
            messages.error(request, "Organization not found.")
            return redirect('home')



# assign members to the project

# assign manager 

@login_required
def assign_manager_to_project(request, organization_id, project_id):
   
    organization = get_object_or_404(Organization, id=organization_id)
    project = get_object_or_404(Project, id=project_id, organization=organization)

 
    profile = get_object_or_404(Profile, user=request.user, organization=organization)
    if not profile.is_admin:
        return redirect('unauthorized_access')  


    if request.method == 'POST':
        form = AssignManagerForm(request.POST, organization=organization) 
        if form.is_valid():
            
            manager_assignment = form.save(commit=False)
            manager_assignment.project = project  
            manager_assignment.save()
            return redirect('org_detail',org_id=organization_id)
    else:
        form = AssignManagerForm(organization=organization)  

    return render(request, 'project/assign_users_to_project.html', {'form': form, 'organization': organization, 'project': project})


# view assigned managers to the project
@login_required
def assigned_manager_detail(request, organization_id, project_id):
    # Get the organization and project
    organization = get_object_or_404(Organization, id=organization_id)
    project = get_object_or_404(Project, id=project_id, organization=organization)

    # Ensure the user is an admin of the organization
    profile = get_object_or_404(Profile, user=request.user, organization=organization)
    if not profile.is_admin:
        return redirect('unauthorized_access')  # Redirect if not authorized

    # Fetch the manager assignment for the given project
    manager_assignment = ProjectManagerAssignment.objects.filter(project=project).select_related('manager').first()

    # Fetch all employees assigned to this manager in the current project
    employee_assignments = ProjectEmployeeAssignment.objects.filter(project=project, manager=manager_assignment.manager) if manager_assignment else []

    if request.method == 'POST':
        if 'remove_manager' in request.POST:
            # Remove the manager from the project
            if manager_assignment:
                manager_assignment.delete()
            return redirect('assigned_manager_detail', organization_id=organization.id, project_id=project.id)
        
        if 'remove_employee' in request.POST:
            # Get the employee assignment to remove
            employee_id = request.POST.get('employee_id')
            employee_assignment = get_object_or_404(ProjectEmployeeAssignment, id=employee_id, project=project, manager=manager_assignment.manager)
            # Remove the employee assignment from the manager without deleting the employee profile
            employee_assignment.delete()
            return redirect('assigned_manager_detail', organization_id=organization.id, project_id=project.id)

    return render(
        request,
        'project/assigned_managers.html',
        {
            'organization': organization,
            'project': project,
            'manager_assignment': manager_assignment,
            'employee_assignments': employee_assignments, 
        },
    )


# Assign employees to a manager within a project
@login_required
def assign_employee_to_manager(request, organization_id, project_id, manager_id):
    
    organization = get_object_or_404(Organization, id=organization_id)
    profile = get_object_or_404(Profile, user=request.user, organization=organization)
    if not profile.is_admin:
        return redirect('unauthorized_access')  

    project = get_object_or_404(Project, id=project_id, organization=organization)
    manager = get_object_or_404(Profile, id=manager_id, is_manager=True, organization=organization)

    # Handle employee assignment
    if request.method == 'POST':
        employee_ids = request.POST.getlist('employee')
        for employee_id in employee_ids:
            employee = get_object_or_404(Profile, id=employee_id, is_employee=True, organization=organization)
            ProjectEmployeeAssignment.objects.get_or_create(project=project, manager=manager, employee=employee)

        # Redirect back to the manager assignment page
        return redirect('assigned_manager_detail', organization_id=organization.id, project_id=project.id)

 
    employees = Profile.objects.filter(organization=organization, is_employee=True)
    
    return render(
        request,
        'project/assign_employees.html',
        {
            'organization': organization,
            'project': project,
            'manager': manager,
            'employees': employees,
        },
    )



# project manager and employee view 
@login_required
def view_projects(request, organization_id):
    # Get the organization
    organization = get_object_or_404(Organization, id=organization_id)
    user_profile = Profile.objects.filter(user=request.user, organization=organization).first()

 
    if not user_profile:
        return HttpResponseForbidden("You do not have permission to view projects in this organization.")

  
    if user_profile.is_admin:
        projects = Project.objects.filter(organization=organization).distinct()
    elif user_profile.is_manager:
        manager_assignments = ProjectManagerAssignment.objects.filter(manager=user_profile)
        projects = Project.objects.filter(projects_assignments__in=manager_assignments).distinct()
    elif user_profile.is_employee:
        employee_assignments = ProjectEmployeeAssignment.objects.filter(employee=user_profile)
        projects = Project.objects.filter(id__in=employee_assignments.values('project')).distinct()
    else:
        return HttpResponseForbidden("You do not have permission to view projects in this organization.")

    return render(request, 'project/project_view.html', {
        'organization': organization,
        'projects': projects,
        'user_profile': user_profile,
    })

# remove employees 


@csrf_exempt
@login_required
def remove_employee_from_project(request, project_id, employee_id):
    # Get the project and employee
    project = get_object_or_404(Project, id=project_id)
    employee_profile = get_object_or_404(Profile, id=employee_id)

    # Check if the user is a manager of the project
    user_profile = Profile.objects.filter(user=request.user, organization=project.organization).first()
    if not user_profile or not user_profile.is_manager:
        return HttpResponseForbidden("You do not have permission to remove employees from this project.")

    # Ensure the manager is assigned to the project
    if not ProjectManagerAssignment.objects.filter(project=project, manager=user_profile).exists():
        return HttpResponseForbidden("You are not assigned as a manager for this project.")

    # Remove the employee from the project
    ProjectEmployeeAssignment.objects.filter(project=project, employee=employee_profile).delete()

    return JsonResponse({'success': 'Employee removed successfully.'})




# project details
@csrf_exempt
@login_required
def project_details(request, organization_id, project_id):
    # Fetch organization and project
    organization = get_object_or_404(Organization, id=organization_id)
    project = get_object_or_404(Project, id=project_id, organization=organization)
    profile = get_object_or_404(Profile, user=request.user, organization=organization)

    # Check if the user is a manager or employee
    if profile.is_manager:
        # Fetch employees assigned to this manager in this project
        employees = Profile.objects.filter(
            employee_assignments__project=project,
            employee_assignments__manager=profile
        ).distinct()
        response = {
            'role': 'manager',
            'project': {
                'name': project.name,
                'description': project.description,
                'start_date': project.start_date,
                'end_date': project.end_date,
            },
            'employees': [{'name': emp.user.get_full_name(), 'username': emp.user.username} for emp in employees]
        }
    elif profile.is_employee:
    
        manager_assignment = ProjectManagerAssignment.objects.filter(project=project).select_related('manager').first()
        employees = Profile.objects.filter(
            employee_assignments__project=project
        ).distinct()

     
        manager_name = None
        if manager_assignment:
            manager_name = manager_assignment.manager.user.get_full_name() or manager_assignment.manager.user.username

        response = {
            'role': 'employee',
            'project': {
                'name': project.name,
                'description': project.description,
                'start_date': project.start_date,
                'end_date': project.end_date,
            },
            'manager': manager_name,  
            'employees': [{'name': emp.user.get_full_name(), 'username': emp.user.username} for emp in employees]
        }
    else:
        return JsonResponse({'error': 'Unauthorized access'}, status=403)

    return JsonResponse(response)






#  CALENDAR PART 



class CalendarRoomView(View):
    template_name = 'calendar+/calendar_room.html'

    def get(self, request):
        return render(request, self.template_name)




# new implementation of availability 
from .forms import AvailabilityForm
import logging
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime


# manage availability for each organizations by diffrent types 

# Display users availability

class AvailabilityDetailView(DetailView):
    model = Availability
    template_name ='availability/detail.html'
    context_object_name = 'availability'

    def get_object(self):
        user = self.request.user
        organization_id = self.kwargs.get('organization_id')
        return get_object_or_404(
            Availability, user=user , organization_id = organization_id
        )



















"""  AVAILABILITY HAS BEEN ENDED """


# HOLIDAYS SECTION
from .models import Holiday
class HolidaySelectionView(View):
    template_name = "holidays/holiday_section.html"

    def get(self, request, *args, **kwargs):
        holidays = Holiday.objects.filter(user=request.user)
        holiday_dates = [
            {
                "start": holiday.start_date.strftime('%Y-%m-%d'),
                'id':holiday.id,
                "end": holiday.end_date.strftime('%Y-%m-%d') if holiday.end_date else holiday.start_date.strftime('%Y-%m-%d'),
                "title": holiday.description or "Holiday",
            }
            for holiday in holidays
        ]
        return render(request, self.template_name, {"holiday_dates": holiday_dates})


@csrf_exempt
def create_holiday(request):
    if request.method == 'POST':
        try:
            # Using request.POST to get form data (not JSON)
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            description = request.POST.get('description', '')

            if not start_date or not end_date:
                return JsonResponse({"error": "Start date and end date are required!"}, status=400)

            holiday = Holiday.objects.create(
                user=request.user,
                start_date=start_date,
                end_date=end_date,
                description=description,
            )

            return JsonResponse({"message": "Holidays added successfully!"}, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)




# holiday detail

@csrf_exempt
def holiday_detail(request, holiday_id):
    holiday = get_object_or_404(Holiday, id=holiday_id)
    
    holiday_data = {
        "start_date": holiday.start_date.strftime('%Y-%m-%d'),
        "end_date": holiday.end_date.strftime('%Y-%m-%d') if holiday.end_date else holiday.start_date.strftime('%Y-%m-%d'),
        "description": holiday.description,
    }
    
    return JsonResponse(holiday_data)


# delete holiday

@csrf_exempt
@login_required  
def delete_holiday(request, holiday_id):
    try:
      
        holiday = get_object_or_404(Holiday, id=holiday_id)
        if holiday.user != request.user:
            return JsonResponse({'error': 'You do not have permission to delete this holiday.'}, status=403)
        holiday.delete()
        return JsonResponse({'message': 'Holiday deleted successfully.'})
    except Holiday.DoesNotExist:
        return JsonResponse({'error': 'Holiday not found.'}, status=404)


# Event Creation

# select event type and host

# step 1) select event type
class EventTypeView(FormView):
    template_name ='events/event_type.html'
    form_class = EventTypeForm

    def form_valid(self, form):
        # save selected event type in session

        event_type = form.cleaned_data['event_type']
        self.request.session['event_type'] = event_type
        return redirect('select_event_host')
    
#  step 2) select host
class SelectEventHostView(TemplateView):
    template_name = 'events/select_event_host.html'

    def get_context_data(self, **kwargs):
        user = self.request.user  
        context = super().get_context_data(**kwargs)
        context['user'] = user 
        return context

    def post(self, request, *args, **kwargs):
    
        selected_host_id = request.POST.get('selected_host')
        if selected_host_id:
            request.session['host_id'] = selected_host_id  
            return redirect('create_event')  
        return redirect('select_event_host') 

# step 3) handle event creation
class CreateEventView(LoginRequiredMixin,FormView):
    template_name = 'events/create_event.html'
    form_class = EventForm

    def get_initial(self):
        initial = super().get_initial()
        initial['user'] = self.request.user
        initial['event_type'] = self.request.session.get('event_type', 'one_on_one')  
        return initial

    def form_valid(self, form):
        event = form.save(commit=False)
        event.user = self.request.user
        event.event_type = self.request.session.get('event_type', 'one_on_one')  
        event.save()
        self.event_id = event.id  

        
        event_link = self.request.build_absolute_uri(reverse('event_detail', kwargs={'event_id': self.event_id}))

        # Redirect the user to the EventDetailView
        return redirect('event_detail', event_id=self.event_id)

    def get_success_url(self):
        return reverse('event_detail', kwargs={'event_id': self.event_id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event_type'] = self.request.session.get('event_type', 'one_on_one')
        return context


# step4 ) event details and booking page
class EventDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'events/event_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = get_object_or_404(Event, id=self.kwargs['event_id'])
        
  
        context['event'] = event
        host = event.user
        context['host_id'] = host.id
        context['invitees'] = event.user
        
        # Generate the event link
        event_link = self.request.build_absolute_uri(reverse('booking_page', kwargs={'event_id': event.id}))
        context['event_link'] = event_link

        return context
    
# working on 

@login_required
def user_availability(request):
    try:
        selected_date = request.GET.get('date')
        if not selected_date:
            return JsonResponse({"error": "No date provided."}, status=400)

        selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        day_of_week = selected_date.strftime('%A')

        holidays = Holiday.objects.filter(user=request.user)
        for holiday in holidays:
            if holiday.is_recurring and holiday.start_date.strftime('%m-%d') == selected_date.strftime('%m-%d'):
                return JsonResponse({"message": "You are unavailable on this date due to a holiday."}, status=200)
            elif not holiday.is_recurring and holiday.start_date <= selected_date <= (holiday.end_date or holiday.start_date):
                return JsonResponse({"message": "You are unavailable on this date due to a holiday."}, status=200)

        availabilities = Availability.objects.filter(user=request.user)
        events = []
        for availability in availabilities:
            if availability.is_recurring and availability.day_of_week == day_of_week:
                events.append({
                    "start_time": availability.start_time.strftime('%I:%M %p') if availability.start_time else "N/A",
                    "end_time": availability.end_time.strftime('%I:%M %p') if availability.end_time else "N/A",
                    "meeting_duration": availability.meeting_duration,
                })
            elif not availability.is_recurring and availability.start_time and availability.start_time.date() == selected_date:
                events.append({
                    "start_time": availability.start_time.strftime('%I:%M %p') if availability.start_time else "N/A",
                    "end_time": availability.end_time.strftime('%I:%M %p') if availability.end_time else "N/A",
                    "meeting_duration": availability.meeting_duration,
                })

        if not events:
            return JsonResponse({"message": "No availability found for this date."}, status=200)

        return JsonResponse(events, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def highlighted_dates(request):
    try:
     
        availabilities = Availability.objects.filter(user=request.user)
        data = [
            {
                "start_time": availability.start_time.isoformat(),
                "end_time": availability.end_time.isoformat(),
            }
            for availability in availabilities
        ]
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# edit event 
@csrf_exempt
def edit_event(request, event_slug):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        event = get_object_or_404(Event, slug=event_slug)  
        form = EventEditForm(request.POST, instance=event) 

        if form.is_valid():
            form.save()  
            return JsonResponse({"success": True, "message": "Event updated successfully!"})
        else:
            return JsonResponse({"success": False, "message": form.errors}) 
    else:
        return JsonResponse({"success": False, "message": "Invalid request."})

# other user side view to book that slot
class BookingPageView(LoginRequiredMixin,TemplateView):
    template_name = 'events_booking/booking_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event_id = self.kwargs['event_id']

        event = get_object_or_404(Event, id=event_id)

        context['event'] = event
        context['host'] = event.user

        return context
    

# Get Event Hosts Availability And Holidays
@login_required
def get_host_availability(request, event_id):
    """
    Fetches the availability slots for the host of the given event.
    It considers both recurring and non-recurring availability for the given date.
    It also checks for holidays and blocks booking on those dates.
    """
    event = get_object_or_404(Event, id=event_id)
    host_availability = Availability.objects.filter(user=event.user)
    holidays = Holiday.objects.filter(user=event.user)

    selected_date = request.GET.get('date', None)
    availability_slots = []

    if selected_date:
        try:
            selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
            day_of_week = selected_date.strftime('%A')  

            print(f"Fetching availability for {event.user.username} on {selected_date}")

            # Check if the selected date is a holiday
            is_holiday = holidays.filter(
                Q(start_date__lte=selected_date, end_date__gte=selected_date) | 
                Q(is_recurring=True, start_date__day=selected_date.day, start_date__month=selected_date.month)  # Recurring holiday
            ).exists()

            if is_holiday:
                return JsonResponse({"message": f"{event.user.username} is not available on {selected_date} due to a holiday."}, status=200)

          
            for availability in host_availability:
                if not availability.start_time or not availability.end_time:
                    print(f"Skipping availability with invalid times: {availability}")
                    continue

               
                start_datetime = datetime.combine(selected_date, availability.start_time)
                end_datetime = datetime.combine(selected_date, availability.end_time)

                if availability.is_recurring and availability.day_of_week == day_of_week:
                    while start_datetime < end_datetime:
                        next_end_time = start_datetime + timedelta(minutes=30)
                        if next_end_time <= end_datetime:
                            availability_slots.append({
                                "start": start_datetime.strftime('%I:%M %p'),
                                "end": next_end_time.strftime('%I:%M %p'),
                                "title": "Available Slot",
                                "isAvailability": True,
                            })
                        start_datetime = next_end_time

                elif not availability.is_recurring and availability.start_time.date() == selected_date:
                    while start_datetime < end_datetime:
                        next_end_time = start_datetime + timedelta(minutes=30)
                        if next_end_time <= end_datetime:
                            availability_slots.append({
                                "start": start_datetime.strftime('%I:%M %p'),
                                "end": next_end_time.strftime('%I:%M %p'),
                                "title": "Available Slot",
                                "isAvailability": True,
                            })
                        start_datetime = next_end_time

            if not availability_slots:
                return JsonResponse({"message": "No availability slots found for this date."}, status=200)

            return JsonResponse(availability_slots, safe=False)

        except ValueError as e:
            print(f"Error parsing date: {e}")
            return JsonResponse({"error": "Invalid date format."}, status=400)
        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "No date provided."}, status=400)




# Handle the booking
class BookEventView(LoginRequiredMixin,FormView):
    template_name = 'events_booking/book_event.html'
    form_class = BookingForm

    def dispatch(self, request, *args, **kwargs):
        self.event = get_object_or_404(Event, pk=kwargs['event_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = self.event

        slots_param = self.request.GET.get('slots', '[]')
        try:
            context['selected_slots'] = json.loads(slots_param)
        except json.JSONDecodeError:
            context['selected_slots'] = []
        return context

    def form_valid(self, form):
        selected_slots = self.request.POST.get('slots')

        if selected_slots:
            # Decode the selected slots
            selected_slots = json.loads(selected_slots)
            if selected_slots:
                first_slot = selected_slots[0]
                start_time_str = first_slot['start']
                end_time_str = first_slot['end']

                today = timezone.now().date()

                start_time = datetime.strptime(f"{today} {start_time_str}", "%Y-%m-%d %I:%M %p")
                end_time = datetime.strptime(f"{today} {end_time_str}", "%Y-%m-%d %I:%M %p")

                booking = Booking.objects.create(
                    event=self.event,
                    event_host=self.event.user,
                    invitee=self.request.user,
                    start_time=start_time,
                    end_time=end_time,
                    status='pending'
                )
                
                # notify the event host
                self.send_event_host_email(booking)

                # notify the invitee
                self.send_invitee_email(booking)

                return redirect('booking_confirmation', booking_id=booking.id)
            else:
                form.add_error(None, 'No slots selected.')
                return self.form_invalid(form)
        else:
            form.add_error(None, 'No slots data found.')
            return self.form_invalid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))
    

    # notify both the users
    def send_event_host_email(self,booking):
        subject =f"New Booking for Your Event: {booking.event.title}"
        message = render_to_string(
            'events_notify/host_booking_email.html',
            {'booking':booking, 'event':booking.event}
        )

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [booking.event_host.email],
            fail_silently=False
        )

    def send_invitee_email(self,booking):
        subject =  f"Booking Confirmation for Event: {booking.event.title}"
        message = render_to_string(
            'events_notify/invitee_booking_email.html',
            {'booking':booking,'event':booking.event}
        )

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL, 
            [booking.invitee.email],
            fail_silently=False,
        )


# Booking Confirmation

class BookingConfirmationView(LoginRequiredMixin,TemplateView):
    template_name ='events_booking/booking_confirmation.html'

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        booking = get_object_or_404(Booking, pk=kwargs['booking_id'])
        context['booking'] = booking
        booking.confirm()
        return context
    

# cancel the booking
class CancelBookingView(View):
    def post(self, request, *args, **kwargs):
        booking = get_object_or_404(Booking, pk=kwargs['booking_id'])

        if booking.user != request.user:
            return JsonResponse({'error':'You are not authorized to cancel this booking'})
        
        booking.cancel()
        return JsonResponse({'message':'Booking has been cancelled successfully'})
    

# display user events and bookings

class UserEventsView(ListView):
    model = Event
    template_name = "events_database/event_list.html"
    context_object_name = "events"

    def get_queryset(self):
        return Event.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)


        context['events_by_location'] = {
            location: self.get_queryset().filter(location=location)
            for location, _ in Event.LOCATION_CHOICES
        }

      
        context['bookings_by_user'] = Booking.objects.filter(invitee=self.request.user).select_related('event', 'event__user')

        return context
    
# event details
class EventDetailsView(DetailView):
    model = Event
    template_name = "events_database/event_details.html"
    context_object_name = "event"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['location_icon'] = self.object.get_location_icon()
        return context

# event bookings 

class EventBookingsView(ListView):
    model = Booking
    template_name = "events_database/event_bookings.html"
    context_object_name = "bookings"

    def get_queryset(self):
        event = get_object_or_404(Event, pk=self.kwargs['pk'])
        return Booking.objects.filter(event=event).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = get_object_or_404(Event, pk=self.kwargs['pk'])
        return context


# delete event

def delete_event(request, event_id):
    event= get_object_or_404(Event,pk=event_id)
    try:
        event.delete()
        messages.success(request,'event has been deleted successfully')
        return redirect('event_list')
    except Exception as e:
        return JsonResponse({'exception':str(e)}, status= 401)
    


# booking Details
class BookingDetailsView(DetailView):
    model = Booking
    template_name = 'events_database/booking_details.html'
    context_object_name = 'booking'  
    pk_url_kwarg = 'booking_id'  


# cancel bookings made by user
class CancelUserBookings(View):
    def post(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id)
        try:
            booking.delete()
            messages.success(request,'booking slot has been deleted')
            return redirect('event_list')
        except Exception as e:
            return JsonResponse({'message':str(e)}, status=401)
            

# booking details made by user 
class BookingDetailsViewUser(View):
    template_name = 'events_database/booking_details_user.html'

    def get(self, request, booking_id):
        booking = get_object_or_404(Booking, pk=booking_id)
        
        if booking.invitee != request.user:
            return render(request, "403.html", status=403)

        return render(request, self.template_name, {'booking': booking})


""" The End of events creation """

# MANAGE AVAILABILITY

# set up the calendar 

# Class for rendering the calendar page


class CalendarView(LoginRequiredMixin, View):
    template_name = 'calendar+/calendar.html'

    def get(self, request):
        return render(request, self.template_name)
    
class AvailabilityCalendarView(View):
    def get(self, request, *args, **kwargs):
        user = request.user  
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
                    "backgroundColor": "#28a745",  
                    "borderColor": "#28a745",
                    "isAvailability": True,  
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
     
        users_with_valid_availability = User.objects.filter(
            availabilities__day_of_week__isnull=False,
            availabilities__start_time__isnull=False,
            availabilities__end_time__isnull=False
        ).distinct()

   
        user_organizations = Organization.objects.filter(profiles__user=request.user)

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
    


@login_required
def fetch_user_availability(request, user_id):
    try:
        availabilities = Availability.objects.filter(user_id=user_id)
        holidays = Holiday.objects.filter(user_id=user_id)
        events = []

        # Mapping day_of_week to FullCalendar dow (0 = Sunday, 6 = Saturday)
        day_map = {
            "Sunday": 0,
            "Monday": 1,
            "Tuesday": 2,
            "Wednesday": 3,
            "Thursday": 4,
            "Friday": 5,
            "Saturday": 6,
        }

   
        holiday_periods = []
        for holiday in holidays:
            if holiday.end_date:
            
                current_date = holiday.start_date
                while current_date <= holiday.end_date:
                    holiday_periods.append(current_date)
                    current_date += timedelta(days=1)
            else:
                holiday_periods.append(holiday.start_date)


        for availability in availabilities:
            
            today = datetime.today().date()
            start_datetime = datetime.combine(today, availability.start_time)
            end_datetime = datetime.combine(today, availability.end_time)

           
            if start_datetime.date() in holiday_periods:
                continue 

            
            availability_day = day_map.get(availability.day_of_week)
            holiday_on_same_day = False

            for holiday in holidays:
                holiday_start_date = holiday.start_date
                holiday_end_date = holiday.end_date or holiday.start_date

                
                if holiday_start_date.weekday() == availability_day or holiday_end_date.weekday() == availability_day:
                    holiday_on_same_day = True
                    break

            if holiday_on_same_day:
                continue  

            event_data = {
                "title": "Available",
                "color": "green" if availability.is_recurring else "blue", 
                "dayOfWeek": availability.day_of_week,
                "startTime": start_datetime.strftime('%H:%M:%S'),
                "endTime": end_datetime.strftime('%H:%M:%S'),
                "recurring": availability.is_recurring,
                "isBooked": availability.is_booked,
            }

            if availability.is_recurring:
                event_data.update({
                    "dow": [day_map[availability.day_of_week]],  
                })
            else:
            
                event_data.update({
                    "start": f"{start_datetime.strftime('%Y-%m-%dT%H:%M:%S')}",
                    "end": f"{end_datetime.strftime('%Y-%m-%dT%H:%M:%S')}",
                })

            events.append(event_data)

        
        for holiday in holidays:
            if holiday.end_date:
                current_date = holiday.start_date
                last_date=holiday.end_date
                while current_date <= holiday.end_date:
                    event_data = {
                        "title": f"Holiday: {holiday.description}",
                        "color": "red",  
                        "start": f"{current_date.strftime('%Y-%m-%d')}T00:00:00",
                        "end": f"{last_date.strftime('%Y-%m-%d')}T23:59:59",
                        "isHoliday": True,
                        "holidayDescription": holiday.description,
                    }
                    events.append(event_data)
                    current_date += timedelta(days=1)
            else:
        
                event_data = {
                    "title": f"Holiday: {holiday.description}",
                    "color": "red", 
                    "start": f"{holiday.start_date.strftime('%Y-%m-%d')}T00:00:00",
                    "end": f"{holiday.end_date.strftime('%Y-%m-%d')}T23:59:59",
                    "isHoliday": True,
                    "holidayDescription": holiday.description,
                }
                events.append(event_data)

        return JsonResponse(events, safe=False)

    except Exception as e:
        print(f"Error fetching availability or holidays for user {user_id}: {e}")
        return JsonResponse({"error": "An error occurred while fetching availability or holidays."}, status=500)



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
           
            user = User.objects.get(id=user_id)

           
            availability = Availability.objects.filter(
                user=user,
                day_of_week=day_of_week,
                start_time=start_time,
                end_time=end_time,
                is_booked=False  
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
                    creator=request.user,  
                )

               
                availability.is_booked = True
                availability.save()

                
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
    meetings = Meets.objects.filter(user=user) | Meets.objects.filter(creator=user) | Meets.objects.filter(participants=user)

    events = []
    today = datetime.today()

   
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
            continue 
        meeting_weekday = weekday_mapping[weekday_name]

        # Calculate the days ahead for the meeting
        days_ahead = (meeting_weekday - today.weekday()) % 7
        meeting_date = today + timedelta(days=days_ahead)
        
    
        start_datetime = meeting_date.replace(hour=meeting.start_time.hour, minute=meeting.start_time.minute)
        end_datetime = meeting_date.replace(hour=meeting.end_time.hour, minute=meeting.end_time.minute)

      
        event_data = {
            'id':meeting.id,
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


class ShareCalendarView(View):
  def post(self, request, user_id):
    form = ShareCalendarForm(request.POST)
    if form.is_valid():
        email = form.cleaned_data['email']
        calendar_link = f"http://127.0.0.1:8000/features_calendar/view-user-calendar/{user_id}/"

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



# CUSTOM REMINDERS FOR MEETINGS
class SetReminderView(LoginRequiredMixin, View):
    """
    Class-Based View for setting a reminder for an existing meeting.
    """
    def get(self, request, meeting_id, *args, **kwargs):
       
        meeting = get_object_or_404(Meets, id=meeting_id)
        # Initialize the reminder form
        reminder_form = ReminderForm()
        return render(request, 'calendar+/set_reminder.html', {'meeting': meeting, 'reminder_form': reminder_form})

    def post(self, request, meeting_id, *args, **kwargs):
    
        meeting = get_object_or_404(Meets, id=meeting_id)
        # Initialize the reminder form with POST data
        reminder_form = ReminderForm(request.POST)

        if reminder_form.is_valid():
            # Create a new reminder for the meeting
            reminder_time = reminder_form.cleaned_data['reminder_time']
            reminder = Reminder.objects.create(
                meeting=meeting,
                user=request.user,
                reminder_time=reminder_time
            )

            
            return redirect('my_calendar')


        return render(request, 'calendar+/set_reminder.html', {'meeting': meeting, 'reminder_form': reminder_form})
    


"""
iNVITE OTHER USERS IN MEETING
"""

class MeetingInviteView(View):
    template_name ='calendar+/invite_users.html'

    def get(self, request, meeting_id):
        """display the invitation form with a list of all users"""

        meeting = get_object_or_404(Meets, id=meeting_id)
        all_users = User.objects.exclude(id__in=meeting.participants.all())
        return render(request, self.template_name, {'meeting':meeting,'all_users':all_users})
    

    def post(self, request, meeting_id):
     """Handle the invitation submission."""
     meeting = get_object_or_404(Meets, id=meeting_id)
     invited_user_ids = request.POST.getlist('invited_users')  # List of user IDs from the checkboxes
     if not invited_user_ids:
        messages.error(request, "No users selected for invitation.")
        return redirect('invite-users', meeting_id=meeting_id)

    # Invite each user
     invited_users = User.objects.filter(id__in=invited_user_ids)
     for user in invited_users:
        invitation, created = MeetInvitation.objects.get_or_create(
            meeting=meeting,
            invited_by=request.user,
        )
        invitation.invited_users.add(user)

         
        self.send_invitation_email(user, meeting)
 
     messages.success(request, "Users successfully invited.")
     return redirect('invite-users', meeting_id=meeting_id)
    
    def send_invitation_email(self, user, meeting):
        """Send an email to the invited user with meeting details."""
        subject = f"You're invited to the meeting: {meeting.title}"

    
        context = {
            'user': user,
            'meeting': meeting,
            'invited_by': meeting.creator,
            'start_time': meeting.start_time,
            'end_time': meeting.end_time,
            'day_of_week': meeting.day_of_week,
        }


        html_message = render_to_string('calendar+/meeting_invitation_email.html', context)

     
        send_mail(
            subject, 
            '',  
            settings.DEFAULT_FROM_EMAIL, 
            [user.email],  
            fail_silently=False, 
            html_message=html_message 
        )
     
    

"""
Accept or Reject the invitation

"""

class InvitationListView(View):
    def get(self, request):
    
        invitations = MeetInvitation.objects.filter(invited_users=request.user)
        return render(request, 'calendar+/meeting_invitations.html', {'invitations': invitations})

    def post(self, request, invitation_id, action):
     
        invitation = get_object_or_404(MeetInvitation, id=invitation_id)
        
        if action == 'accept':
            if invitation.accept_invitation(request.user):
                messages.success(request, "Invitation accepted.")
            else:
                messages.error(request, "Unable to accept invitation.")
        elif action == 'reject':
            if invitation.reject_invitation(request.user):
                messages.success(request, "Invitation rejected.")
            else:
                messages.error(request, "Unable to reject invitation.")
        
        return redirect('meeting-invitations')  
    
""" Empty invitation box """

def empty_meets(request):
    try:
   
        invitations_to_delete = MeetInvitation.objects.filter(
            invited_by=request.user
        ) | MeetInvitation.objects.filter(
            invited_users__id=request.user.id
        )

        for invitation in invitations_to_delete:
            
            invitation.invited_users.remove(request.user)

       
            if invitation.invited_users.count() == 0:
                invitation.delete()

        messages.success(request, 'Your invitations have been truncated successfully.')
        return redirect('meeting-invitations')
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=400)
    



class MeetingInviteView(View):
    template_name ='calendar+/invite_users.html'

    def get(self, request, meeting_id):

        """display the invitation form with a list of all users"""

        meeting = get_object_or_404(Meets, id=meeting_id)
        all_users = User.objects.exclude(id__in=meeting.participants.all())
        return render(request, self.template_name, {'meeting':meeting,'all_users':all_users})
    

    def post(self, request, meeting_id):
     """Handle the invitation submission."""
     meeting = get_object_or_404(Meets, id=meeting_id)
     invited_user_ids = request.POST.getlist('invited_users')  
     if not invited_user_ids:
        messages.error(request, "No users selected for invitation.")
        return redirect('invite-users', meeting_id=meeting_id)

   
     invited_users = User.objects.filter(id__in=invited_user_ids)
     for user in invited_users:
        invitation, created = MeetInvitation.objects.get_or_create(
            meeting=meeting,
            invited_by=request.user,
        )
        invitation.invited_users.add(user)

      
        self.send_invitation_email(user, meeting)
 
     messages.success(request, "Users successfully invited.")
     return redirect('invite-users', meeting_id=meeting_id)
    
    def send_invitation_email(self, user, meeting):
        """Send an email to the invited user with meeting details."""
        subject = f"You're invited to the meeting: {meeting.title}"

      
        context = {
            'user': user,
            'meeting': meeting,
            'invited_by': meeting.creator,
            'start_time': meeting.start_time,
            'end_time': meeting.end_time,
            'day_of_week': meeting.day_of_week,
        }

        html_message = render_to_string('calendar+/meeting_invitation_email.html', context)

     
        send_mail(
            subject,  
            '',  
            settings.DEFAULT_FROM_EMAIL, 
            [user.email],  
            fail_silently=False,  
            html_message=html_message  
        )
     

    """  Analytics view """

# analytics section


class AnalyticsDashboardView(TemplateView):
    template_name = "analytics/dashboard.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 1. Total number of meetings per user
        meetings_per_user = Meets.objects.values('user__username').annotate(meeting_count=Count('user')).order_by('-meeting_count')
        # 2. Available time slots per day
        availability_per_day = Availability.objects.values('day_of_week').annotate(available_count=Count('id')).order_by('day_of_week')
        # 3. Meetings created by each user
        meetings_created_by_user = Meets.objects.values('creator__username').annotate(meetings_created=Count('creator')).order_by('-meetings_created')
        # 4. Recurring vs Non-recurring availability
        recurring_count = Availability.objects.filter(is_recurring=True).count()
        non_recurring_count = Availability.objects.filter(is_recurring=False).count()

        #  Average meeting duration per user
        # Convert Python objects to JSON string
        context['meetings_per_user'] = json.dumps(list(meetings_per_user))
        context['availability_per_day'] = json.dumps(list(availability_per_day))
        context['meetings_created_by_user'] = json.dumps(list(meetings_created_by_user))
        context['recurring_count'] = recurring_count
        context['non_recurring_count'] = non_recurring_count
      
        return context


# organization analysis

class OrganizationSelectView(TemplateView):
    template_name = 'analytics/org_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # fetch all organizations where user is an admin
        context['organizations'] = Organization.objects.filter(
            profiles__user=self.request.user,
            profiles__is_admin=True
        ).distinct()

        return context
    
# accept id and do analysis on organization 
def organization_analysis(request, org_id):
    # Fetch the organization
    organization = Organization.objects.get(id=org_id)
    
    # Get profiles in the organization and their role distribution
    profiles = Profile.objects.filter(organization=organization)
    
   
    role_distribution = profiles.values('is_admin', 'is_manager', 'is_employee').aggregate(
        admins=Count('is_admin', filter=Q(is_admin=True)),
        managers=Count('is_manager', filter=Q(is_manager=True)),
        employees=Count('is_employee', filter=Q(is_employee=True))
    )
    
    invitation_status = EmailInvitation.objects.filter(organization=organization).values('status').annotate(
        count=Count('status')
    ).order_by('status')
    
    invitation_dates = EmailInvitation.objects.filter(organization=organization).values('expires_at').annotate(
        count=Count('id')
    ).order_by('expires_at')
    

    profile_by_role = profiles.values('is_admin', 'is_manager', 'is_employee').annotate(
        count=Count('user')
    ).order_by('-count')
    
  
    expiry_distribution = EmailInvitation.objects.filter(organization=organization).values('expires_at').annotate(
        count=Count('id')
    ).order_by('expires_at')
   
    profile_creation_dates = Profile.objects.filter(organization=organization).values('user__date_joined').annotate(
        count=Count('id')
    ).order_by('user__date_joined')
    
 
    pending_accepted_invites = EmailInvitation.objects.filter(organization=organization).values('status').annotate(
        count=Count('id')
    ).filter(status__in=['pending', 'accepted'])
    
   
    role_activity = EmailInvitation.objects.filter(organization=organization).values('role').annotate(
        count=Count('id')
    ).order_by('role')


    chart_data = {
        'role_distribution': {
            'admins': role_distribution['admins'],
            'managers': role_distribution['managers'],
            'employees': role_distribution['employees']
        },
        'invitation_status': list(invitation_status),
        'invitation_dates': list(invitation_dates),
        'profile_by_role': list(profile_by_role),
        'expiry_distribution': list(expiry_distribution),
        'profile_creation_dates': list(profile_creation_dates),
        'pending_accepted_invites': list(pending_accepted_invites),
        'role_activity': list(role_activity),
    }


    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse(chart_data)

  
    return render(request, 'analytics/organization_analytics.html', {
        'org_id': org_id,
    })



# filter meetings like calendly 

"""  Filter meetings to get easiear  """



class MeetsView(View):
    template_name ='meets/meets.html'

    def get(self, request):
        user = request.user
        current_time = now()

        """ Get all meets  """

        meets = Meets.objects.filter(
            participants = user
        ) | Meets.objects.filter(user=user) | Meets.objects.filter(creator = user)

        """ categorize meets """

        upcoming_meets = meets.filter(start_time__gte=current_time).order_by('start_time')
        past_meets = meets.filter(end_time__lt=current_time).order_by('end_time')

       
        pending_meets = meets.filter(start_time__gte=current_time, day_of_week='Pending')

        

        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        meets_in_range = None
        if start_date and end_date:
            try:
                start_date_obj =datetime.strptime(start_date, "%Y-%m-%d").date()
                end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
                meets_in_range = meets.filter(
                    start_time_date__gte = start_date_obj,
                    end_time__date__lte = end_date_obj,
                ).order_by('start_time')

            except ValueError:
                meets_in_range = []



        context = {
            "upcoming_meets": upcoming_meets,
            "past_meets": past_meets,
            "pending_meets": pending_meets,
            "meets_in_range": meets_in_range,
        }
        return render(request, self.template_name, context)          




def get_meet_details(request):
    meet_id = request.GET.get('id')

    if not meet_id:
        return JsonResponse({"error": "Meeting ID not provided"}, status=400)

    try:
        meet = Meets.objects.get(id=meet_id)
    except Meets.DoesNotExist:
        return JsonResponse({"error": "Meeting not found"}, status=404)

    
    creator = meet.creator.username if meet.creator else "No creator"
    user = meet.user.username if meet.user else "No user assigned"

   
    participants = ", ".join([user.username for user in meet.participants.all()])

    
    data = {
        "title": meet.title,
        "description": meet.description or "No description available",
        "start_time": meet.start_time.strftime("%H:%M"),
        "end_time": meet.end_time.strftime("%H:%M"),
        "participants": participants,
        "day_of_week": meet.day_of_week,
        "creator": creator,
        "user": user,
    }

    return JsonResponse(data)





@csrf_exempt
def filter_meets(request):
    if request.method == "GET":
        start_time = request.GET.get("start_time")
        end_time = request.GET.get("end_time")

        if not start_time or not end_time:
            return JsonResponse({"error": "Start time and end time are required."}, status=400)

        try:
            start_time = datetime.fromisoformat(start_time)
            end_time = datetime.fromisoformat(end_time)
        except ValueError:
            return JsonResponse({"error": "Invalid datetime format."}, status=400)

        if start_time > end_time:
            return JsonResponse({"error": "Start time cannot be later than end time."}, status=400)

        filtered_meets = Meets.objects.filter(
            Q(start_time__gte=start_time, start_time__lte=end_time) |
            Q(end_time__gte=start_time, end_time__lte=end_time),
            Q(participants=request.user) | Q(created_by=request.user)
        ).values("id", "title", "start_time", "end_time", "user__username")

        return JsonResponse({"meets": list(filtered_meets)}, status=200)



""" Contact list where user will add users in his contacts """

# CONTACT LIST

class IntroContacts(LoginRequiredMixin,View):
    template_name ='contacts/intro_contacts.html'

    def get(self, request):
        return render(request,self.template_name)
   
class ContactListView(View):
    def get(self, request, *args, **kwargs):
        contacts = Contacts.objects.filter(user=request.user).select_related('contact_user')
        favorite_ids = FavoriteContact.objects.filter(user=request.user).values_list('contact_id', flat=True)
        context = {
            'contacts': contacts,
            'favorite_ids': set(favorite_ids),  
        }
        return render(request, 'contacts/my_cont.html', context)
    

@csrf_exempt
def add_to_favorite(request):
    if request.method == "POST":
        try:
           
            data = json.loads(request.body)
            contact_id = data.get("contact_id")
            user = request.user

         
            if not contact_id:
                return JsonResponse({"status": "error", "message": "Contact ID not provided."}, status=400)

            
            try:
                contact_entry = Contacts.objects.get(id=contact_id, user=user)
            except Contacts.DoesNotExist:
                return JsonResponse({"status": "error", "message": "Contact not found in your list."}, status=404)

          
            if FavoriteContact.objects.filter(user=user, contact=contact_entry.contact_user).exists():
                return JsonResponse({"status": "exists", "message": "Contact is already in favorites."})

            # Add to favorites
            FavoriteContact.objects.create(user=user, contact=contact_entry.contact_user)
            return JsonResponse({"status": "added", "message": f"{contact_entry.contact_user.username} added to favorites."})

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)



# Favourite contacts
class FavoriteContactsView(ListView):
    model = FavoriteContact
    template_name = 'contacts/favourite_contacts.html'
    context_object_name = 'favorite_contacts'

    def get_queryset(self):

        return FavoriteContact.objects.filter(user=self.request.user)
    
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        
        contact_id = request.POST.get('contact_id')
        if contact_id:
            try:
                user = self.request.user
                contact = User.objects.get(id=contact_id)
                favorite_contact = FavoriteContact.objects.get(user=user, contact=contact)
                favorite_contact.delete()

                messages.success(request,'contact removed successfully')
                return redirect('favorite-contacts')
            except FavoriteContact.DoesNotExist:
                return JsonResponse({"success": False, "message": "Favorite contact not found."})
            except User.DoesNotExist:
                return JsonResponse({"success": False, "message": "User not found."})

        return JsonResponse({"success": False, "message": "Invalid request."})



class RemoveFavoriteView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        contact_id = request.POST.get('contact_id')
        if contact_id:
            try:
               
                user = request.user
                contact = User.objects.get(id=contact_id)
                favorite_contact = FavoriteContact.objects.get(user=user, contact=contact)
                
              
                favorite_contact.delete()

                return JsonResponse({"success": True, "message": "Removed from favorites successfully."})
            except FavoriteContact.DoesNotExist:
                return JsonResponse({"success": False, "message": "Contact is not in favorites."})
            except User.DoesNotExist:
                return JsonResponse({"success": False, "message": "User not found."})

        return JsonResponse({"success": False, "message": "Invalid request."})



class ContactBookView(TemplateView):
    template_name = 'contacts/contact_list.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
       
       
        meeting_users_ids = Meets.objects.filter(
            Q(creator=user) | Q(participants=user) | Q(user=user)
        ).exclude(user=user).distinct().values('user')
        users_with_meetings = User.objects.filter(id__in=meeting_users_ids)
        user_orgs = {}
     
        context.update({
          
            'users_with_meetings': users_with_meetings,
        
          
        })
        return context
    def post(self, request, *args, **kwargs):
       
        contact_ids = request.POST.getlist('contact_ids')  
        user = request.user
        for contact_id in contact_ids:
            contact_user = User.objects.get(id=contact_id)
            Contacts.objects.get_or_create(user=user, contact_user=contact_user)
            messages.success(request, 'user added to your contact list successfully')
            return redirect('select_contact')
        return self.get(request, *args,   **kwargs)

