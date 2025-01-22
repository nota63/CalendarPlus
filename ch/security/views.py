
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.http import Http404
from accounts.models import Profile, Organization, EventOrganization, BookingOrganization, MeetingOrganization
from .models import ActivityLog, Action
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import ActionSelectionForm
from django.db import models 
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.db.models import Prefetch
from django.views import View

# Security view
def security_view(request, org_id):

    organization = get_object_or_404(Organization, id=org_id)


    try:
        profile = organization.profiles.get(user=request.user)
        if not profile.is_admin:
            raise PermissionDenied("You do not have permission to access this page.")
    except Profile.DoesNotExist:
        raise PermissionDenied("You do not have permission to access this page.")

    
    activity_logs = (
        ActivityLog.objects.filter(organization=organization)
        .select_related('admin', 'target_user')
        .prefetch_related('actions')
    )

  
    email = request.GET.get('email')
    if email:
       
        return redirect('confirm_security', org_id=org_id, email=email)

  
    context = {
        'organization': organization,
        'activity_logs': activity_logs,
    }
    return render(request, 'security/security.html', context)




# Security delete
def delete_user_actions(request, org_id, email):

    organization = get_object_or_404(Organization, id=org_id)

    try:
        admin_profile = Profile.objects.get(user=request.user, organization=organization, is_admin=True)
    except Profile.DoesNotExist:
        messages.error(request, "You do not have the necessary permissions to perform this action.")
        return redirect('security', org_id=org_id)

    
    try:
        target_profile = Profile.objects.get(user__email=email, organization=organization)
        target_user = target_profile.user
    except Profile.DoesNotExist:
        messages.error(request, "No user with this email is found in your organization! Try with another email.")
        return redirect('security', org_id=org_id)

    
    if request.method == 'POST':
        form = ActionSelectionForm(request.POST)
        if form.is_valid():
            selected_actions = form.cleaned_data['actions']

        
            activity_log = ActivityLog.objects.create(
                organization=organization,
                admin=request.user,
                target_user=target_user,
                action_details="User actions were performed.",
            )

          
            action_objects = Action.objects.filter(name__in=selected_actions)

            try:
               
                if 'delete_meetings' in selected_actions:
                    MeetingOrganization.objects.filter(invitee=target_user, organization=organization).delete()

                if 'delete_events' in selected_actions:
                    EventOrganization.objects.filter(user=target_user, organization=organization).delete()

                if 'delete_bookings' in selected_actions:
                    BookingOrganization.objects.filter(invitee=target_user, organization=organization).delete()

               
                messages.success(request, f"Successfully deleted selected actions for {target_user.email}.")

                
                activity_log.actions.set(action_objects)
                activity_log.save()

            except Exception as e:
                messages.error(request, f"An error occurred while performing the actions: {str(e)}")
                return redirect('security', org_id=org_id)

            return redirect('confirm_security', org_id=organization.id, email=email)

    else:
        form = ActionSelectionForm()

    context = {
        'organization': organization,
        'target_user': target_user,
        'form': form,
        'email': email,
    }

    return render(request, 'security/confirm_security_actions.html', context)



# managed Workflows
class ManagedWorkflows(View):
    template_name = 'security/managed_workflows.html'

    def get(self, request, org_id):
        user = self.request.user
        try:
            # Fetch the organization, ensuring the user is the creator
            organization = Organization.objects.get(id=org_id, created_by=user)
        except Organization.DoesNotExist:
            raise Http404("Organization not found or you do not have permission to view this organization.")
        
        context = {
            'organization': organization
        }
        return render(request, self.template_name, context)
    
    def post(self, request, org_id):
        
        pass
