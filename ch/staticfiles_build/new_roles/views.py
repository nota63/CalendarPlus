from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Profile
from .forms import ProfileForm
from django.views import View
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages

# Create your views here.

def feature_implementation(request):
    return render(request,'new_roles/features.html')


class AddUserView(View):
    template = 'new_roles/add_user.html'

    def get(self, request):
        # ensure the user is authorized manager or admin
        if not hasattr(request.user, 'profile') or not (
            request.user.profile.is_profile_admin() or request.user.profile.is_manager()
        ):
            return HttpResponseForbidden('Not Allowed!')

        form = ProfileForm()
        return render(request, self.template, {'form': form})

    def post(self, request):
        # Ensure the user is authorized (admin or manager)
        if not hasattr(request.user, 'profile') or not (
            request.user.profile.is_profile_admin() or request.user.profile.is_manager()
        ):
            return HttpResponseForbidden('Not Allowed!')

        form = ProfileForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            if request.user.profile.is_profile_admin():
                # Admins can add managers or employees
                if new_user.role == 'admin':
                    return HttpResponseForbidden('Admins cannot create other admins!')
            elif request.user.profile.is_manager():
                # Managers can only add employees
                if new_user.role != 'employee':
                    return HttpResponseForbidden('Managers can only add employees!')

            try:
                new_user.save()
                messages.success(request, f'{new_user.role.capitalize()} added successfully!')
                return redirect('add_user')  
            except Exception as e:
                return JsonResponse({'exception': str(e)}, status=500)
        return render(request, self.template, {'form': form})


# display users 

class ProfileListView(View):
    template_name= 'new_roles/profile_list.html'

    def get(self, request):
        # ensure the user has a profile
        if not hasattr(request.user, 'profile'):
            return HttpResponseForbidden('Not allowed!')
        
        # admin can see all profiles (managers and employees)
        if request.user.profile.is_profile_admin():
            profiles = Profile.objects.all()

        # manager can only see employees 
        elif request.user.profile.is_manager():
            profiles = Profile.objects.filter(role='employee')

        # if the user is neigther admin nor manager 
        else:
            return HttpResponseForbidden('Not Allowed')

        return render(request,self.template_name,{'profiles':profiles})
    
    @staticmethod
    def delete_profile(request, profile_id):
        # Ensure the user has a profile
        if not hasattr(request.user, 'profile'):
            return HttpResponseForbidden('Not Allowed!')

        # Get the profile to be deleted
        profile_to_delete = get_object_or_404(Profile, id=profile_id)

        # Admin can delete both managers and employees
        if request.user.profile.is_profile_admin():
            # Only allow deletion of another user's profile
            if profile_to_delete != request.user.profile:
                profile_to_delete.delete()
                messages.success(request, f'Profile of {profile_to_delete.full_name} deleted successfully.')
            else:
                messages.error(request, 'You cannot delete your own profile.')
        
        # Manager can only delete employees
        elif request.user.profile.is_manager() and profile_to_delete.role == 'employee':
            # Only allow deletion of employee profiles
            if profile_to_delete != request.user.profile:
                profile_to_delete.delete()
                messages.success(request, f'Profile of {profile_to_delete.full_name} deleted successfully.')
            else:
                messages.error(request, 'You cannot delete your own profile.')
        
        # If the user is neither admin nor manager, deny access
        else:
            return HttpResponseForbidden('Not Allowed!')

        return redirect('profile_list')
            


# ORGANIZATION 
from .forms import OrganizationForm
from .models import Organization
from .forms import AddUserToOrganizationForm
from django.db.models import Q

class AddToOrganizationView(View):
    template = 'new_roles/add_to_organization.html'

    def get(self, request, pk):
        # Ensure user has permission to manage the organization
        organization = Organization.objects.get(pk=pk)

        if not request.user.profile.is_profile_admin() and not organization.manager == request.user.profile:
            return HttpResponseForbidden('Not Allowed!')

        form = OrganizationForm(instance=organization)
        return render(request, self.template, {'form': form, 'organization': organization})

    def post(self, request, pk):
        organization = Organization.objects.get(pk=pk)

        if not request.user.profile.is_profile_admin() and not organization.manager == request.user.profile:
            return HttpResponseForbidden('Not Allowed!')

        form = OrganizationForm(request.POST, instance=organization)
        if form.is_valid():
            role = form.cleaned_data['role']
            profile = form.cleaned_data['profile']

            if role == 'manager':
                organization.manager = profile
            elif role == 'employee':
                organization.employees.add(profile)

            organization.save()
            messages.success(request, f'{role.capitalize()} added to {organization.organization_name} successfully!')
            return redirect('organization_detail', pk=organization.pk)

        return render(request, self.template, {'form': form, 'organization': organization})


# organization list view

class OrganizationListView(View):
    template_name = 'new_roles/organization_list.html'

    def get(self, request):
        # Ensure the user has a profile
        if not hasattr(request.user, 'profile'):
            return HttpResponseForbidden('Not Allowed!')

        user_profile = request.user.profile

        # Fetch organizations where the user is an admin or a manager
        organizations = Organization.objects.filter(
            Q(admin=user_profile) | Q(manager=user_profile)
        ).distinct()

        if not organizations:
            return HttpResponseForbidden('You are not associated with any organizations as admin or manager.')

        return render(request, self.template_name, {'organizations': organizations})
    
# organization detail
class OrganizationDetailView(View):
    template_name = 'new_roles/organization_detqail.html'

    def get(self, request, pk):
        # Ensure the user is the admin of the requested organization
        if not hasattr(request.user, 'profile'):
            return HttpResponseForbidden('Not Allowed!')

        organization = get_object_or_404(Organization, pk=pk)

        # Check if the logged-in user is the admin of this specific organization
        if organization.admin != request.user.profile and organization.manager != request.user.profile:
            return HttpResponseForbidden('You are not authorized to view this organization.')

        return render(request, self.template_name, {'organization': organization})


# add user to organization
class AddUserToOrganizationView(View):
    template_name = 'new_roles/add_user_to_organization.html'

    def get(self, request, pk):
        organization = get_object_or_404(Organization, pk=pk)
        
        # Check permissions
        if not self._has_permission(request.user, organization):
            return HttpResponseForbidden("You don't have permission to manage this organization.")
        
        form = AddUserToOrganizationForm()
        return render(request, self.template_name, {'form': form, 'organization': organization})

    def post(self, request, pk):
        organization = get_object_or_404(Organization, pk=pk)
        
        # Check permissions
        if not self._has_permission(request.user, organization):
            return HttpResponseForbidden("You don't have permission to manage this organization.")
        
        form = AddUserToOrganizationForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            role = form.cleaned_data['role']

            # Assign manager or employee based on role
            if role == 'manager':
                if organization.manager:  # Only one manager allowed
                    messages.error(request, "This organization already has a manager.")
                    return redirect('organization_list')
                organization.manager = user
            elif role == 'employee':
                organization.employees.add(user)

            organization.save()
            messages.success(request, f'{user.full_name} has been added as {role}.')
            return redirect('organization_list')
        
        return render(request, self.template_name, {'form': form, 'organization': organization})

    @staticmethod
    def _has_permission(user, organization):
        # Organization admin or manager can access this view
        return (
            user.profile == organization.admin or
            user.profile == organization.manager
        )
    

# user profile 

class UserProfileView(View):
    template_name = 'new_roles/user_profile.html'

    def get(self, request):
        # the user should has a profile
        if not hasattr(request.user, 'profile'):
            return HttpResponseForbidden('Profile not found / you are not a part of the company')

        user_profile = request.user.profile

        # fetch the organization where user is associated
        organizations_as_admin = Organization.objects.filter(admin=user_profile)
        organizations_as_manager= Organization.objects.filter(manager=user_profile)
        organizations_as_employee = Organization.objects.filter(employees=user_profile)

        context = {
            'profile':user_profile,
            'organizations_as_admin':organizations_as_admin,
            'organizations_as_manager':organizations_as_manager,
            'organizations_as_employee':organizations_as_employee
        }
        return render(request,self.template_name, context)
       


# permissions    




