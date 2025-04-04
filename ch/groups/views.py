from django.shortcuts import render, redirect , get_object_or_404
from django.urls import reverse
from .models import Group, GroupMember, GroupInvitation, GroupEvent, GroupEventBooking, GroupEventReminder, GroupActivity
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from formtools.wizard.views import SessionWizardView
from django.http import HttpResponseRedirect
from accounts.models import Organization, Profile
from .forms import GroupNameForm,GroupDescriptionForm,TeamLeaderForm
from django.core.exceptions import PermissionDenied
from formtools.wizard.views import SessionWizardView
from django.http import Http404
from django.views.generic import ListView
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils.timezone import now
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse
from datetime import datetime 
from django.db import models
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from django.utils.timezone import now, make_aware
from django.utils.html import format_html
from .models import AbsentEvent
from django.utils import timezone
from django.utils.timezone import localtime
from group_tasks.models import Task
# Create your views here.
FORMS = [
    ("name", GroupNameForm),
    ("description", GroupDescriptionForm),
    ("team_leader", TeamLeaderForm),
]

TEMPLATES = {
    "name": "groups/wizard_name.html",
    "description": "groups/wizard_description.html",
    "team_leader": "groups/wizard_team_leader.html",
}

class GroupCreationWizard(SessionWizardView):
    form_list = FORMS
    template_name = "groups/wizard_form.html"
    storage_name = "formtools.wizard.storage.session.SessionStorage"

    def dispatch(self, request, *args, **kwargs):
      
        self.org_id = kwargs.get('org_id')
        self.organization = get_object_or_404(Organization, id=self.org_id)

    
        profile = Profile.objects.filter(user=request.user, organization=self.organization, is_admin=True).first()
        if not profile:
            raise PermissionDenied("You are not authorized to create groups for this organization.")

        return super().dispatch(request, *args, **kwargs)

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):
       
        data = {form_name: form.cleaned_data for form_name, form in zip(self.get_form_list().keys(), form_list)}
        name = data['name']['name']
        description = data['description']['description']
        email = data['team_leader']['email']

   
        team_leader_profile = Profile.objects.filter(
            user__email=email, organization=self.organization
        ).first()
        if not team_leader_profile:
            form = self.get_form('team_leader')
            form.add_error('email', "The email does not belong to any member of this organization.")
            return self.render_revalidation_failure({'team_leader': form})

        
        group = Group.objects.create(
            organization=self.organization,
            name=name,
            description=description,
            team_leader=team_leader_profile.user,
            created_by=self.request.user
        )

        GroupActivity.objects.create(
                organization=group.organization,
                group=group,
                user=self.request.user,
                action_type='GROUP_CREATED',
                details=f"Group '{group.name}' created by {group.created_by}.",
            )


        return redirect('display_groups/',org_id=self.organization.id)
    



# Display the groups to the admin
class GroupListView(ListView):
    model = Group
    template_name = 'groups/display_groups.html'
    context_object_name = 'groups'
    
    def get_queryset(self):
        org_id = self.kwargs.get('org_id')
        
   
        organization = get_object_or_404(Organization, id=org_id)
        # restrict access
        if not Profile.objects.filter(user=self.request.user, organization=organization):
            return HttpResponseForbidden("Unauthorized Accesss")

        
        if not self.request.user.profiles.filter(organization=organization, is_admin=True).exists():
            raise Http404("You are not an admin of this organization.")

        return Group.objects.filter(organization=organization, created_by=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        org_id = self.kwargs.get('org_id')
        
        organization = get_object_or_404(Organization, id=org_id)
        context['organization'] = organization
        
        return context





# Invite members into the group!
@login_required
def invite_members_to_group(request, org_id, group_id):
    try:
        
        organization = Organization.objects.get(id=org_id)
        group = Group.objects.get(id=group_id, organization=organization)
        # restrict access
        if not Profile.objects.filter(user=request.user, organization=organization):
            return HttpResponseForbidden("Unauthorized Accesss")


    
    
        profile = Profile.objects.get(user=request.user, organization=organization)
        is_admin = profile.is_admin
        is_team_leader = group.team_leader == request.user

        if not (is_admin or is_team_leader):
            raise PermissionDenied

    except (Organization.DoesNotExist, Group.DoesNotExist, Profile.DoesNotExist):
        return HttpResponse("Organization or Group not found.", status=404)

    if request.method == 'POST':
        emails = request.POST.get('emails')
        email_list = emails.split(',')  
        
   
        for email in email_list:
            email = email.strip()
            try:
                
                user = User.objects.get(email=email)
                if not Profile.objects.filter(user=user, organization=organization).exists():
                    raise ValidationError(f"Email {email} does not belong to an organization member.")
            except User.DoesNotExist:
                raise ValidationError(f"No user found with email: {email}")

      
            if not GroupInvitation.objects.filter(recipient_email=email, group=group).exists():
                invitation = GroupInvitation.objects.create(
                    group=group,
                    sender=request.user,
                    recipient_email=email
                )

                GroupActivity.objects.create(
                   organization=group.organization,
                   group=group,
                   user=invitation.sender,
                   action_type='INVITED_MEMBER',
                   details=f"{invitation.sender} invited {invitation.recipient_email} in group {group.name}",
               )
                 
                invite_link = request.build_absolute_uri(
                    f'/groups/invite/{org_id}/{group_id}/{invitation.id}/accept/'
                )
                send_mail(
                    subject=f"Invitation to join {group.name}",
                    message=f"Hello! You are invited to join the group {group.name}. Click the link to accept or reject the invitation:\n{invite_link}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                )
                messages.success(request, f"Invitation sent to {email}.")
            else:
                messages.warning(request, f"An invitation to {email} has already been sent.")

        return redirect('display_groups', org_id=org_id)

    return render(request, 'groups/invite_members.html', {'group': group})



# Accept or reject the invitation
def accept_or_reject_invitation(request, org_id, group_id, invitation_id):
    invitation = get_object_or_404(GroupInvitation, id=invitation_id, group_id=group_id)
    organization = get_object_or_404(Organization, id=org_id)
    # restrict access
    if not Profile.objects.filter(user=request.user, organization=organization):
        return HttpResponseForbidden("Unauthorized Accesss")


   
    if invitation.group.organization.id != org_id:
        messages.error(request, "Invalid invitation link.")
        return redirect('home')


    if not Profile.objects.filter(user=request.user, organization=invitation.group.organization).exists():
        messages.error(request, "You are not a part of this organization.")
        return redirect('home')

    if invitation.invitation_status != 'pending':
        messages.info(request, "This invitation has already been responded to.")
        return redirect('home')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'accept':
            # Add user to the group
            if not GroupMember.objects.filter(group=invitation.group, user=request.user).exists():
                GroupMember.objects.create(
                    group=invitation.group,
                    user=request.user,
                    organization=organization,
                    role=invitation.role
                )

                GroupActivity.objects.create(
                   organization=organization,
                   group=invitation.group,
                   user=request.user,
                   action_type='INVITATION_ACCEPT',
                   details=f"{request.user} accepted the invitation for {invitation.role} in group {invitation.group}",
                )
                invitation.invitation_status = 'accepted'
                invitation.invited_user = request.user
                invitation.organization=organization
                invitation.save()
                messages.success(request, f"You have successfully joined {invitation.group.name}.")
            else:
                messages.warning(request, "You are already a member of this group.")

        elif action == 'reject':
         
            invitation.invitation_status = 'rejected'
            invitation.save()
            GroupActivity.objects.create(
                   organization=organization,
                   group=invitation.group,
                   user=request.user,
                   action_type='INVITATION_REJECT',
                   details=f"{request.user} rejected the invitation for {invitation.role} in group {invitation.group}",
                )
            messages.success(request, "You have rejected the invitation.")

# redirection is pending!!
        return redirect('home')

    return render(request, 'groups/accept_reject_invitation.html', {'invitation': invitation})



# ------------------------------------------------------------------------------------------------------------------------------------------------------


# Members side features for groups and actions


# display the groups
from django.db.models import Q


@login_required
def user_groups(request, org_id):
    organization = get_object_or_404(Organization, id=org_id)
    # restrict access
    if not Profile.objects.filter(user=request.user, organization=organization):
        return HttpResponseForbidden("Unauthorized Accesss")



    if not organization.profiles.filter(user=request.user).exists():
        return redirect('home')

 
    user_groups = Group.objects.filter(
        Q(organization=organization) & (Q(members__user=request.user) | Q(team_leader=request.user))
    ).distinct()


    team_leader_groups = user_groups.filter(team_leader=request.user)

    print("Found Team Leader Groups:", team_leader_groups) 

    return render(request, 'user_groups/user_groups.html', {
        'organization': organization,
        'user_groups': user_groups,
        'team_leader_groups': team_leader_groups,
    })




# Team Leader

@login_required
def manage_group_users(request, org_id, group_id):
   
    organization = get_object_or_404(Organization, id=org_id)
    group = get_object_or_404(Group, id=group_id, organization=organization)
    # restrict access
    if not Profile.objects.filter(user=request.user, organization=organization):
        return HttpResponseForbidden("Unauthorized Accesss")
    
    # Fetch the most recent invitation for the group
    most_recent_invitation = GroupInvitation.objects.filter(group=group_id).order_by('-invitation_sent_at').first()

    if most_recent_invitation:
        invited_user = most_recent_invitation.invited_user
        username = invited_user.username if invited_user else None
        profile = Profile.objects.filter(user=invited_user, organization=organization).first()
        profile_picture = profile.profile_picture if profile else None
    else:
        username = None
        profile_picture = None
       # Fetch the count of invitations with each status
    status_counts = GroupInvitation.objects.filter(group=group).values('invitation_status').annotate(count=Count('id'))
    total_invitations=GroupInvitation.objects.filter(group=group).count()

    # Convert to a dictionary for easy access
    status_dict = {status['invitation_status']: status['count'] for status in status_counts}

    # Get the count for each status, defaulting to 0 if not found
    pending_count = status_dict.get('pending', 0)
    accepted_count = status_dict.get('accepted', 0)
    rejected_count = status_dict.get('rejected', 0)
    


   
    if group.team_leader != request.user:
        return redirect('user_groups', org_id=org_id)  


    members = GroupMember.objects.filter(group=group)

    return render(request, 'user_groups/manage_group_users.html', {
        'organization': organization,
        'group': group,
        'members': members,
        'username': username,
        'profile_picture': profile_picture,
        'pending_count':pending_count,
        'accepted_count':accepted_count,
        'rejected_count':rejected_count,
        "total_invitations":total_invitations,
       
    })





# Remove the user from the grop

# team leader can access this view 
from django.http import HttpResponseForbidden
@login_required
def remove_user_from_group(request, org_id, group_id, user_id):
   
    organization = get_object_or_404(Organization, id=org_id)
    group = get_object_or_404(Group, id=group_id, organization=organization)
    user_to_remove = get_object_or_404(User, id=user_id)
    # restrict access
    if not Profile.objects.filter(user=request.user, organization=organization):
        return HttpResponseForbidden("Unauthorized Accesss")


    if group.team_leader != request.user:
        return HttpResponseForbidden("You are not authorized to remove members from this group.")

    
    try:
        group_member = GroupMember.objects.get(group=group, user=user_to_remove)
    except GroupMember.DoesNotExist:
        return redirect('user_groups', org_id=org_id)  

    group_member.delete()
    GroupActivity.objects.create(
                   organization=organization,
                   group=group,
                   user=request.user,
                   action_type='MEMBER_DISCARD',
                   details=f"{request.user} removed {group_member.user} from group {group} in group.",
                )

 
    return redirect('manage_group_users', org_id=org_id , group_id=group.id)



# Team leader Event Creation
@login_required
def create_group_event(request, org_id, group_id):
   
    organization = get_object_or_404(Organization, id=org_id)
    group = get_object_or_404(Group, id=group_id, organization=organization)
    # restrict access
    if not Profile.objects.filter(user=request.user, organization=organization):
        return HttpResponseForbidden("Unauthorized Accesss")


    if group.team_leader != request.user:
        return HttpResponseForbidden("You do not have permission to create events for this group.")
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        date = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        meeting_link = request.POST.get('meeting_link')
        location = request.POST.get('location')
        slots = request.POST.get('slots')

        
        if not title or not date or not start_time or not end_time or not location:
            messages.error(request, "Please fill in all required fields.")
            return redirect('create_group_event', org_id=org_id, group_id=group_id)

        
        group_event = GroupEvent.objects.create(
            group=group,
            organization=organization,
            created_by=request.user,
            title=title,
            description=description,
            date=date,
            start_time=start_time,
            end_time=end_time,
            meeting_link=meeting_link,
            location=location,
            slots=slots,
            created_at=now(),
        )

        GroupActivity.objects.create(
                   organization=organization,
                   group=group,
                   user=request.user,
                   action_type='CREATE_EVENT',
                   details=f"{request.user} created event {group_event.title}.",
                )

      
        group_members = GroupMember.objects.filter(group=group)
        
 
        subject = f"New Event Created: {title} in {group.name}"
        message = f"""
        Hello,

        A new event has been created for your group, {group.name}, in the {organization.name} organization.

        Event Details:
        Title: {title}
        Description: {description if description else 'No description provided.'}
        Date: {date}
        Time: {start_time} to {end_time}
        Location: {location}
        Meeting Link: {meeting_link if meeting_link else 'Not provided'}

        We hope to see you there!

        Regards,
        {organization.name} Team
        """

    
        for group_member in group_members:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[group_member.user.email],
            )

        messages.success(request, "Group event created and invitations sent successfully!")
        return redirect('user_groups', org_id=org_id) 

    return render(request, 'group_events/create_event.html', {
        'group': group,
        'organization': organization
    })





# Display the created events to all the Group Members 
@login_required
def display_group_events(request, org_id, group_id):
 
    organization = get_object_or_404(Organization, id=org_id)
    group = get_object_or_404(Group, id=group_id, organization=organization)
    # restrict access
    if not Profile.objects.filter(user=request.user, organization=organization):
        return HttpResponseForbidden("Unauthorized Accesss")


    if not GroupMember.objects.filter(group=group, organization=organization, user=request.user).exists() and not group.team_leader == request.user:
        return HttpResponseForbidden("You do not have permission to view events for this group.")

    events = GroupEvent.objects.filter(group=group).order_by('-created_at')

    is_team_leader = group.team_leader == request.user

 
    for event in events:
        event.is_booked_by_user = GroupEventBooking.objects.filter(group_event=event, user=request.user).exists()

    return render(request, 'group_events/display_events.html', {
        'organization': organization,
        'group': group,
        'events': events,
        'is_team_leader':is_team_leader,
    })





# Make Ajax call to book the event

@login_required
@transaction.atomic
def book_group_event(request, org_id, group_id, event_id):
   
    organization = get_object_or_404(Organization, id=org_id)
    group = get_object_or_404(Group, id=group_id, organization=organization)
    event = get_object_or_404(GroupEvent, id=event_id, group=group, organization=organization)
    # restrict access
    if not Profile.objects.filter(user=request.user, organization=organization):
        return HttpResponseForbidden("Unauthorized Accesss")


    
    if not GroupMember.objects.filter(group=group, organization=organization, user=request.user).exists():
        return HttpResponseForbidden("You are not authorized to book this event.")


    current_time = now()

  
    event_datetime = datetime.combine(event.date, event.start_time)
    
    
    event_datetime = make_aware(event_datetime, timezone=current_time.tzinfo)


    if event_datetime <= current_time:
        return JsonResponse({"error": "This event is no longer available for booking."}, status=400)

  
    if GroupEventBooking.objects.filter(group_event=event, user=request.user).exists():
        return JsonResponse({"error": "You have already booked this event."}, status=400)

 
    total_bookings = GroupEventBooking.objects.filter(group_event=event).count()
    if total_bookings >= event.slots:
        return JsonResponse({"error": "No slots are available for this event."}, status=400)
    
   
    if event.slots <= 0:
        return JsonResponse({"error": "No slots are available for this event."}, status=400)

  
    event.slots -= 1
    event.save()

    booking = GroupEventBooking.objects.create(
        group_event=event,
        organization=organization,
        group=group,
        user=request.user,
        booking_date=current_time.date(),
        booking_time=current_time.time(),
        status='confirmed',
    )

    GroupActivity.objects.create(
                   organization=organization,
                   group=group,
                   user=request.user,
                   action_type='BOOK_EVENT',
                   details=f"{request.user} booked the event {event.title} Event created by {event.created_by}.",
                )


    
    user_email = request.user.email
    event_creator_email = event.created_by.email

    subject = f"Event Booking Confirmation: {event.title}"


    user_email_body = format_html("""
        <h3>Dear {user_name},</h3>
        <p>You have successfully booked the event <strong>{event_title}</strong> for {event_date} at {event_time}.</p>
        <p><strong>Event Details:</strong><br>
        Title: {event_title}<br>
        Date: {event_date}<br>
        Time: {event_time}<br>
        Location: {event_location}<br>
        Meeting Link: {meeting_link}</p>
        <p><strong>Organization Details:</strong><br>
        Organization: {organization_name}</p>
    """.format(
        user_name=request.user.username,
        event_title=event.title,
        event_date=event.date,
        event_time=f"{event.start_time} - {event.end_time}",
        event_location=event.location,
        meeting_link=event.meeting_link or "N/A",
        organization_name=organization.name
    ))

 
    creator_email_body = format_html("""
        <h3>Dear {creator_name},</h3>
        <p>The user <strong>{user_name}</strong> has booked the event <strong>{event_title}</strong> for {event_date} at {event_time}.</p>
        <p><strong>Booking Details:</strong><br>
        User: {user_name}<br>
        Event Title: {event_title}<br>
        Date: {event_date}<br>
        Time: {event_time}<br>
        Location: {event_location}</p>
        <p><strong>Organization Details:</strong><br>
        Organization: {organization_name}</p>
    """.format(
        creator_name=event.created_by.username,
        user_name=request.user.username,
        event_title=event.title,
        event_date=event.date,
        event_time=f"{event.start_time} - {event.end_time}",
        event_location=event.location,
        organization_name=organization.name
    ))


    send_mail(
        subject,
        '',
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
        fail_silently=False,
        html_message=user_email_body
    )


    send_mail(
        subject,
        '',
        settings.DEFAULT_FROM_EMAIL,
        [event_creator_email],
        fail_silently=False,
        html_message=creator_email_body
    )

   
    return JsonResponse({
        "message": "Event successfully booked and emails sent!",
        "booking_id": booking.id,
        "status": booking.status,
    }, status=201)


# Absent Event
@login_required
def mark_absent(request, org_id, group_id, event_id):
    organization = get_object_or_404(Organization, id=org_id)
    group = get_object_or_404(Group, id=group_id, organization=organization)
    event = get_object_or_404(GroupEvent, id=event_id, group=group, organization=organization)
    # restrict access
    if not Profile.objects.filter(user=request.user, organization=organization):
        return HttpResponseForbidden("Unauthorized Accesss")


  
    if not GroupMember.objects.filter(group=group, organization=organization, user=request.user).exists():
        return JsonResponse({"error": "You are not a member of this group or organization."}, status=400)

    if AbsentEvent.objects.filter(event=event, user=request.user).exists():
        return JsonResponse({"error": "As per organization rules you can only be absent to one event not more than one!."}, status=400)
    
    if request.method == 'POST':
        
        reason = request.POST.get('reason')
        custom_message = request.POST.get('custom_message')

     
        if not reason:
            return JsonResponse({"error": "Invalid reason selected."}, status=400)

     
        absent_event = AbsentEvent.objects.create(
            organization=organization,
            event=event,
            group=group,
            user=request.user,
            reason=reason,
            custom_message=custom_message,
            date=timezone.now(),
        )

        GroupActivity.objects.create(
                   organization=organization,
                   group=group,
                   event=event,
                   user=request.user,
                   action_type='MARK_ABSENT',
                   details=f"{request.user} marked absent to himself for event {event.title} in group {group.name}",

                )

      
        return JsonResponse({
            "message": f"You have marked yourself as absent for the event: {event.title}.",
            "absent_event_id": absent_event.id
        }, status=201)

    return JsonResponse({"error": "Invalid request method."}, status=405)



# Handle Reminders
@login_required
def set_event_reminder(request, org_id, group_id, event_id):
    
    organization = get_object_or_404(Organization, id=org_id)
    group = get_object_or_404(Group, id=group_id, organization=organization)
    event = get_object_or_404(GroupEvent, id=event_id, group=group, organization=organization)
    # restrict access
    if not Profile.objects.filter(user=request.user, organization=organization):
        return HttpResponseForbidden("Unauthorized Accesss")

    if not GroupMember.objects.filter(group=group, organization=organization, user=request.user).exists():
        return JsonResponse({"error": "You are not a member of this group or organization."}, status=400)


    existing_reminder = GroupEventReminder.objects.filter(event=event, group=group, organization=organization, user=request.user).first()
    if existing_reminder:
        return JsonResponse({"error": "You have already set a reminder for this event."}, status=400)

    if request.method == 'POST':
      
        reminder_option = request.POST.get('reminder_option')
        custom_time = request.POST.get('custom_time')  
        reason = request.POST.get('reason')

        
        if reminder_option not in ['1_day_before', '1_hour_before', 'custom']:
            return JsonResponse({"error": "Invalid reminder option."}, status=400)


        if reminder_option == 'custom' and not custom_time:
            return JsonResponse({"error": "Custom time is required for custom reminder."}, status=400)

        if reminder_option == 'custom':
            try:
                custom_time = timezone.make_aware(timezone.datetime.strptime(custom_time, '%Y-%m-%d %H:%M:%S'))
            except ValueError:
                return JsonResponse({"error": "Invalid custom time format. Please use 'YYYY-MM-DD HH:MM:SS'."}, status=400)

    
        try:
            reminder = GroupEventReminder.objects.create(
                organization=organization,
                group=group,
                event=event,
                user=request.user,
                reminder_options=reminder_option,
                custom_time=custom_time if reminder_option == 'custom' else None,
                reminder_message=f"Reminder: {event.title} is coming up!",
                reason=reason or 'Upcoming',
                is_sent=False
            )

            GroupActivity.objects.create(
                   organization=organization,
                   group=group,
                   event=event,
                   user=request.user,
                   action_type='SET_EVENT_REMINDER',
                   details=f"{request.user} set reminder for event {event.title} in group {group.name}",
                   
                )
            

            
            return JsonResponse({
                "message": f"Reminder set successfully for event: {event.title}.",
                "reminder_id": reminder.id
            }, status=201)

        except IntegrityError:
            return JsonResponse({"error": "Failed to create reminder. Please try again."}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=405)


# Display all users who booked the event!

@login_required
def fetch_event_bookings(request, org_id, group_id, event_id):
    """
    Fetch and return all users who booked a specific group event.
    """
    
    organization = get_object_or_404(Organization, id=org_id)
    group = get_object_or_404(Group, id=group_id, organization=organization)
    event = get_object_or_404(GroupEvent, id=event_id, group=group, organization=organization)
    # restrict access
    if not Profile.objects.filter(user=request.user, organization=organization):
        return HttpResponseForbidden("Unauthorized Accesss")



    if not GroupMember.objects.filter(group=group, organization=organization, user=request.user).exists():
        return JsonResponse({"error": "You are not authorized to view bookings for this event."}, status=403)

    # Fetch all bookings for the event
    bookings = GroupEventBooking.objects.filter(group_event=event).select_related('user')

    print('Bookings Found!:',bookings)

    
    booking_data = [
        {
            "user_id": booking.user.id,
            "user_name": booking.user.get_full_name() or booking.user.username,
            "email": booking.user.email,
            "booking_date": booking.booking_date.strftime('%Y-%m-%d'),
            "booking_time": booking.booking_time.strftime('%H:%M:%S'),
            "status": booking.status,
        }
        for booking in bookings
    ]

    return JsonResponse({"bookings": booking_data}, status=200)


# Event Analytics
from django.db.models import Count

@login_required
def event_analytics(request, org_id, group_id, event_id):
    
    event = get_object_or_404(GroupEvent, id=event_id, organization_id=org_id, group_id=group_id)
    organization = get_object_or_404(Organization, id=org_id)
    # restrict access
    if not Profile.objects.filter(user=request.user, organization=organization):
        return HttpResponseForbidden("Unauthorized Accesss")


    # Total bookings
    total_bookings = GroupEventBooking.objects.filter(group_event=event).count()

    # Bookings by status
    confirmed_bookings = GroupEventBooking.objects.filter(group_event=event, status='confirmed').count()
    pending_bookings = GroupEventBooking.objects.filter(group_event=event, status='pending').count()
    cancelled_bookings = GroupEventBooking.objects.filter(group_event=event, status='cancelled').count()

    # Absentee reasons
    absentee_reasons_query = AbsentEvent.objects.filter(event=event).values('reason').annotate(count=models.Count('reason'))
    absentee_reasons = [{'reason': item['reason'], 'count': item['count']} for item in absentee_reasons_query]

    # Reminders stats
    total_reminders = GroupEventReminder.objects.filter(event=event).count()
    reminder_sent = GroupEventReminder.objects.filter(event=event, is_sent=True).count()
    reminder_pending = GroupEventReminder.objects.filter(event=event, is_sent=False).count()

    # Reminder types breakdown
    reminder_types_query = GroupEventReminder.objects.filter(event=event).values('reminder_options').annotate(count=models.Count('reminder_options'))
    reminder_types = [{'reminder_options': item['reminder_options'], 'count': item['count']} for item in reminder_types_query]

    # Construct the response
    data = {
        'event_title': event.title,
        'event_description': event.description,
        'event_date': event.date,
        'event_start_time': event.start_time,
        'event_end_time': event.end_time,
        'total_bookings': total_bookings,
        'confirmed_bookings': confirmed_bookings,
        'pending_bookings': pending_bookings,
        'cancelled_bookings': cancelled_bookings,
        'absentee_reasons': absentee_reasons,
        'total_reminders': total_reminders,
        'reminder_sent': reminder_sent,
        'reminder_pending': reminder_pending,
        'reminder_types': reminder_types,
    }

    return JsonResponse(data)


# User specific analysis

@login_required
def user_group_event_analytics(request, org_id, group_id, event_id):
   
    event = get_object_or_404(GroupEvent, id=event_id, organization_id=org_id)
    organization = get_object_or_404(Organization, id=org_id)
    # restrict access
    if not Profile.objects.filter(user=request.user, organization=organization):
        return HttpResponseForbidden("Unauthorized Accesss")



    bookings = GroupEventBooking.objects.filter(
        user=request.user, group_event__id=event_id, group_event__organization_id=org_id
    )

 
    absences = AbsentEvent.objects.filter(
        user=request.user, event__id=event_id, event__organization_id=org_id
    )

 
    reminders = GroupEventReminder.objects.filter(
        user=request.user, event__id=event_id, event__organization_id=org_id
    )

 
    total_bookings = bookings.count()
    confirmed_bookings = bookings.filter(status='confirmed').count()
    pending_bookings = bookings.filter(status='pending').count()
    cancelled_bookings = bookings.filter(status='cancelled').count()


    total_absences = absences.count()
    absentee_reasons = absences.values('reason').annotate(count=models.Count('reason'))

    # Calculate reminders data
    total_reminders = reminders.count()
    reminder_sent = reminders.filter(is_sent=True).count()
    reminder_pending = reminders.filter(is_sent=False).count()


    data = {
        'event_title': event.title,
        'event_description': event.description,
        'event_date': event.date,
        'event_start_time': event.start_time,
        'event_end_time': event.end_time,
        'total_bookings': total_bookings,
        'confirmed_bookings': confirmed_bookings,
        'pending_bookings': pending_bookings,
        'cancelled_bookings': cancelled_bookings,
        'total_absences': total_absences,
        'absentee_reasons': list(absentee_reasons),
        'total_reminders': total_reminders,
        'reminder_sent': reminder_sent,
        'reminder_pending': reminder_pending,
    }

    return JsonResponse(data)



# Delete the event!
@csrf_exempt
def delete_group_event(request, org_id, group_id, event_id):
    if request.method == 'POST':
       
        organization = get_object_or_404(Organization, id=org_id)
        group = get_object_or_404(Group, id=group_id, organization=organization)
        event = get_object_or_404(GroupEvent, id=event_id, group=group, organization=organization)
        # restrict access
        if not Profile.objects.filter(user=request.user, organization=organization):
            return HttpResponseForbidden("Unauthorized Accesss")


  
        if request.user != group.team_leader:
            return JsonResponse({'error': 'You do not have permission to delete this event.'}, status=403)

     
        team_leader = group.team_leader

        
        password = request.POST.get('password')

        if not team_leader.check_password(password):
            return JsonResponse({'error': 'Incorrect password.'}, status=400)

 
        event.delete()

        GroupActivity.objects.create(
                   organization=organization,
                   group=group,
                   event=event,
                   user=request.user,
                   action_type='DELETE_EVENT',
                   details=f"{request.user} deleted the event {event.title} from group {group.name}",
                   
                )
        return JsonResponse({'success': 'Event deleted successfully.'})

    return JsonResponse({'error': 'Invalid request method.'}, status=405)



# Handle Recurring Events
@method_decorator([login_required, csrf_exempt], name='dispatch')
class SaveRecurrenceInfoView(View):
    def post(self, request, org_id, group_id, event_id):
        try:
           
            organization = get_object_or_404(Organization, id=org_id)

           
            group = get_object_or_404(Group, id=group_id, organization=organization)
            # restrict access
            if not Profile.objects.filter(user=request.user, organization=organization):
                return HttpResponseForbidden("Unauthorized Accesss")

    
          
            event = get_object_or_404(GroupEvent, id=event_id, group=group, organization=organization)

          
            if group.team_leader != request.user:
                return JsonResponse({'success': False, 'message': 'You are not authorized to perform this action.'}, status=403)

        
            if event.recurrence_type != 'none':
                return JsonResponse({'success': False, 'message': 'Recurrence has already been set for this event.'}, status=400)

         
            recurrence_type = request.POST.get('recurrence_type', 'none')
            recurrence_end_date = request.POST.get('recurrence_end_date')
            recurrence_days = request.POST.get('recurrence_days', '')

            if recurrence_type != 'none' and not recurrence_end_date:
                return JsonResponse({'success': False, 'message': 'Recurrence end date is required for recurring events.'}, status=400)

          
            event.recurrence_type = recurrence_type
            event.recurrence_end_date = recurrence_end_date
            event.recurrence_days = recurrence_days
            event.save()

            GroupActivity.objects.create(
                   organization=organization,
                   group=group,
                   event=event,
                   user=request.user,
                   action_type='RECURRING_EVENT',
                   details=f"{request.user} set the event as recurring to event {event.title} in group {group.name}",
                   
                )
            

            return JsonResponse({'success': True, 'message': 'Recurrence information saved successfully.'})
        except Organization.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Organization not found.'}, status=404)
        except Group.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Group not found.'}, status=404)
        except GroupEvent.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Event not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)


# Implement Search bar
def search_events(request, org_id, group_id):
    search_title = request.GET.get('search_title', '')
    filter_date = request.GET.get('filter_date', '')
    filter_location = request.GET.get('filter_location', '')
    organization = get_object_or_404(Organization,id=org_id)

    # restrict access
    if not Profile.objects.filter(user=request.user, organization=organization):
        return HttpResponseForbidden("Unauthorized Accesss")


    events = GroupEvent.objects.filter(
        organization_id=org_id,
        group_id=group_id
    )

  
    if search_title:
        events = events.filter(title__icontains=search_title)

  
    if filter_date:
        events = events.filter(date=filter_date)


    if filter_location:
        events = events.filter(location=filter_location)

    
    event_data = []
    for event in events:
        event_data.append({
            'id': event.id,
            'title': event.title,
            'date': event.date,
            'start_time': event.start_time,
            'end_time': event.end_time,
            'location': event.location,
            'slots': event.slots,
            'meeting_link': event.meeting_link if event.meeting_link else '',
            'created_at': event.created_at.strftime('%b %d, %Y %I:%M %p'),
            'organization_id': event.organization.id,
            'group_id': event.group.id,
            'created_by': event.created_by.username,
        })

    return JsonResponse({'events': event_data})

# ---------------------------------------------------------------------------------------------------------------------------------------------------------


# Group related actions for team leader and members


class GroupDetailsView(LoginRequiredMixin, View):
    template_name = 'group_actions/group_details.html'

    def get(self, request, org_id, group_id):
     
        organization = get_object_or_404(Organization, id=org_id)
        group = get_object_or_404(Group, id=group_id, organization=organization)

        if request.user != group.created_by and request.user != group.team_leader:
            return render(request, '403.html', {"message": "Access Denied"})
        
        # restrict access
        if not Profile.objects.filter(user=request.user, organization=organization):
          return HttpResponseForbidden("Unauthorized Accesss")


        members = GroupMember.objects.filter(group=group)
        events = GroupEvent.objects.filter(group=group)
        bookings = GroupEventBooking.objects.filter(group_event__group=group)
        absentees = AbsentEvent.objects.filter(group=group)
        reminders = GroupEventReminder.objects.filter(group=group)

    
        total_members = members.count()
        total_bookings = bookings.count()
        total_absentees = absentees.count()
        reminder_sent_count = reminders.filter(is_sent=True).count()
        reminder_pending_count = reminders.filter(is_sent=False).count()

        events_with_bookings = GroupEvent.objects.filter(group=group).annotate(num_bookings=Count('bookings'))
        total_bookings = GroupEventBooking.objects.filter(group_event__group=group).count()

    
        event_labels = [event.title for event in events_with_bookings]
        event_bookings = [event.num_bookings for event in events_with_bookings]
        events_with_users = GroupEvent.objects.annotate(num_users=Count('bookings__user'))
        last_month = timezone.now() - timedelta(days=30)
        user_participation = GroupEventBooking.objects.filter(
         booking_date__gte=last_month
       ).values('user').annotate(events_attended=Count('user')).order_by('-events_attended')
        context = {
            'organization': organization,
            'group': group,
            'members': members,
            'events': events,
            'bookings': bookings,
            'absentees': absentees,
            'reminders': reminders,
            'total_members': total_members,
            'total_bookings': total_bookings,
            'total_absentees': total_absentees,
            'reminder_sent_count': reminder_sent_count,
            'reminder_pending_count': reminder_pending_count,
            'events_with_bookings': events_with_bookings,
            'total_bookings': total_bookings,
             'event_labels': event_labels,
             'event_bookings':event_bookings,
             'events_with_users':events_with_users,
             'last_month':last_month,
             'user_participation':user_participation,
        }
        return render(request, self.template_name, context)


# Group Calendar
class GroupEventView(LoginRequiredMixin, View):
    def get(self, request, org_id, group_id):
    
        group = get_object_or_404(Group, id=group_id, organization_id=org_id)
        organization = get_object_or_404(Organization, id=org_id)
        if not GroupMember.objects.filter(group=group, user=request.user).exists():
            return JsonResponse({'error': 'You are not a member of this group.'}, status=403)
        # restrict access
        if not Profile.objects.filter(user=request.user, organization=organization):
           return HttpResponseForbidden("Unauthorized Accesss")


       
        events = GroupEvent.objects.filter(group=group, organization=organization)

    
        event_data = []
        for event in events:
            event_data.append({
                'title': event.title,
                'start': f'{event.date}T{event.start_time.isoformat()}',
                'end': f'{event.date}T{event.end_time.isoformat()}',
                'description': event.description,
                'location': event.location,
                'meeting_link': event.meeting_link,
            })

        return render(request, 'group_actions/group_event_calendar.html', {
            'group': group,
            'events': event_data
        })
    

# More features 

# Fetch user details 
@login_required
def group_member_details(request, org_id, group_id, user_id):
    organization = get_object_or_404(Organization, id=org_id)
    group = get_object_or_404(Group, id=group_id, organization=organization)


    if group.team_leader != request.user:
        raise PermissionDenied("You are not authorized to view this member.")
    
    # restrict access
    if not Profile.objects.filter(user=request.user, organization=organization):
        return HttpResponseForbidden("Unauthorized Accesss")


    
    group_member = get_object_or_404(GroupMember, group=group, user__id=user_id)

    
    if not group_member.user:
        return JsonResponse({'error': 'The user is not associated with this group!'}, status=400)

    user = group_member.user

   
    joined_at = localtime(group_member.joined_at).strftime("%d %b %Y, %H:%M")

    
    member_details = {
        'username': user.username,
        'email': user.email,
        'role': group_member.role,
        'joined_at': joined_at, 
    }

    return JsonResponse(member_details)

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Admin side features 

# Fetch all group Members 

@csrf_exempt
def fetch_group_members(request, org_id, group_id):
    if request.method == 'GET':
        # Fetch the group and check if it's created by the current user
        group = get_object_or_404(Group, id=group_id, organization_id=org_id)

        if group.created_by != request.user:
            return JsonResponse({'error': 'You are not authorized to view this group'}, status=403)
        
        # restrict access
        if not Profile.objects.filter(user=request.user, organization=group.organization):
           return HttpResponseForbidden("Unauthorized Accesss")


        # Fetch the team leader and group members
        team_leader = group.team_leader
        group_members = GroupMember.objects.filter(group=group)

        members_data = []
        for member in group_members:
            members_data.append({
                'user_id': member.user.id,
                'username': member.user.username,
                'role': member.role,
                'joined_at': member.joined_at,
            })

        # Include the team leader in the response data
        response_data = {
            'team_leader': {
                'user_id': team_leader.id,
                'username': team_leader.username,
                'role': 'team_leader',
            },
            'members': members_data
        }

        return JsonResponse(response_data)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


# Delete the group
@csrf_exempt
def delete_group(request, org_id, group_id):
    if request.method == 'POST':
        group = get_object_or_404(Group, id=group_id, organization_id=org_id)
        # restrict access
        if not Profile.objects.filter(user=request.user, organization=group.organization):
           return HttpResponseForbidden("Unauthorized Accesss")

        if group.created_by == request.user:
          
            GroupActivity.objects.create(
                organization=group.organization,
                group=group,
                user=request.user,
                action_type='GROUP_DELETED',
                details=f"Group '{group.name}' deleted by {request.user.username}.",
            )

         
            group.delete()
            return JsonResponse({'success': True, 'message': 'Group deleted successfully.'})

        else:
            return JsonResponse({'success': False, 'message': 'You are not authorized to delete this group.'})

    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method.'})


# Fetch group activities

class GroupActivityLogView(View):
    def get(self, request, org_id, group_id):
      
        organization = get_object_or_404(Organization, id=org_id)
        group = get_object_or_404(Group, id=group_id, organization=organization)

        # restrict access
        if not Profile.objects.filter(user=request.user, organization=organization):
          return HttpResponseForbidden("Unauthorized Accesss")

        activities = GroupActivity.objects.filter(group=group).order_by('-timestamp')
        if not group.created_by == request.user:
            return HttpResponseForbidden("You do not have permissions to access this feature! please contact your workspace admin!")
          
        activity_data = [
            {
                'user': activity.user.username,
                'action_type': activity.get_action_type_display(),
                'details': activity.details,
                'timestamp': activity.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            }
            for activity in activities
        ]

    
        return JsonResponse({'success': True, 'activities': activity_data})


# MORE FEATURES ARE PENDING........

# manager side features ---------------------------------------------------------------------------------------------------------------

# Fetch group details and the team members
@login_required
def fetch_group_details(request, org_id, group_id):
    # Get the group
    group = get_object_or_404(Group, organization_id=org_id, id=group_id)
    organization = get_object_or_404(Organization, id=org_id)
    # restrict access
    if not Profile.objects.filter(user=request.user, organization=organization):
        return HttpResponseForbidden("Unauthorized Accesss")


    # Get group leader's profile (if exists)
    leader_profile = Profile.objects.filter(user=group.team_leader, organization=organization).first()
    leader_data = {
        "id": group.team_leader.id if group.team_leader else None,
        "name": group.team_leader.username if group.team_leader else group.team_leader.username,
        "profile_picture": leader_profile.profile_picture.url if leader_profile and leader_profile.profile_picture else None
    } if group.team_leader else None

    # Get group members
    members = GroupMember.objects.filter(group=group).select_related("user")
    members_data = [
        {
            "id": member.user.id,
            "name": member.user.username,
            "profile_picture": (Profile.objects.filter(user=member.user, organization=organization).first().profile_picture.url
                                if Profile.objects.filter(user=member.user, organization=organization).exists() and 
                                Profile.objects.filter(user=member.user, organization=organization).first().profile_picture
                                else None)
        }
        for member in members
    ]

    # Return JSON response
    return JsonResponse({
        "group": {
            "id": group.id,
            "name": group.name,
            "description": group.description,
            "team_leader": leader_data,
            "created_at": group.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        },
        "members": members_data
    }, safe=False)


# DISPLAY GROUP DETAILS 
@login_required
def group_details_ajax(request, org_id, group_id):
    # Fetch the organization and group objects
    organization = get_object_or_404(Organization, pk=org_id)
    group = get_object_or_404(Group, pk=group_id, organization=organization)

    # restrict access
    if not Profile.objects.filter(user=request.user, organization=organization):
        return HttpResponseForbidden("Unauthorized Accesss")

    # Fetch the group description and other details
    group_description = group.description
    group_name = group.name
    group_leader = group.team_leader.username if group.team_leader else None

    # Count total events related to this group
    total_events = GroupEvent.objects.filter(group=group).count()

    # Fetch the most recent event
    most_recent_event = GroupEvent.objects.filter(group=group).order_by('-date', '-start_time').first()

    # Count total bookings for this group
    total_bookings = GroupEventBooking.objects.filter(group=group).count()

    # Prepare data to send in JSON response
    response_data = {
        'group_name': group_name,
        'group_description': group_description,
        'group_leader': group_leader,
        'total_events': total_events,
        'total_bookings': total_bookings,
        'most_recent_event': {
            'title': most_recent_event.title if most_recent_event else None,
            'description': most_recent_event.description if most_recent_event else None,
            'date': most_recent_event.date if most_recent_event else None,
            'start_time': most_recent_event.start_time if most_recent_event else None,
            'end_time': most_recent_event.end_time if most_recent_event else None,
            'location': most_recent_event.location if most_recent_event else None,
            'meeting_link': most_recent_event.meeting_link if most_recent_event else None,
        }
    }

    return JsonResponse(response_data)


# Assign The Task (Ajax New)
import json 
from .utils import *

@login_required
def assign_task(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            org_id = data.get("org_id")
            group_id = data.get("group_id")
            email = data.get("email")
            title = data.get("title")
            description = data.get("description", "")
            priority = data.get("priority", "medium")
            deadline = data.get("deadline")
            start_date = data.get("start_date", None)
            end_date = data.get("end_date", None)
            is_recurring = data.get("is_recurring", False)
            recurrence_pattern = data.get("recurrence_pattern", None)
            recurrence_end_date = data.get("recurrence_end_date", None)
            notify_assignee = data.get("notify_assignee", True)
            
            # Validate Organization & Group
            organization = get_object_or_404(Organization, id=org_id)
            group = get_object_or_404(Group, id=group_id, organization=organization)
            
            # Validate User
            user = get_object_or_404(User, email=email)
            
            # Check if the user is a group member
            if not GroupMember.objects.filter(group=group, user=user).exists():
                return JsonResponse({"error": "User is not a member of this group."}, status=400)
            
            # Create Task
            task = Task.objects.create(
                organization=organization,
                group=group,
                created_by=request.user,
                assigned_to=user,
                title=title,
                description=description,
                priority=priority,
                deadline=deadline,
                start_date=start_date,
                end_date=end_date,
                is_recurring=is_recurring,
                recurrence_pattern=recurrence_pattern,
                recurrence_end_date=recurrence_end_date,
                notify_assignee=notify_assignee,
            )
            # Send email to assigned user
            send_task_assigned_email(user, task, organization, group)
            
            
            return JsonResponse({"success": "Task assigned successfully!", "task_id": task.id})
        
        except ValidationError as e:
            return JsonResponse({"error": str(e)}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"error": "Invalid request method."}, status=405)


# Create Group Event 
@login_required
def create_group_event_new(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            org_id = data.get("org_id")
            group_id = data.get("group_id")
            title = data.get("title")
            description = data.get("description", "")
            date = data.get("date")
            start_time = data.get("start_time")
            end_time = data.get("end_time")
            meeting_link = data.get("meeting_link")
            location = data.get("location")
            slots = data.get("slots", 0)
            recurrence_type = data.get("recurrence_type", "none")
            recurrence_end_date = data.get("recurrence_end_date", None)
            recurrence_days = data.get("recurrence_days")

            # Ensure recurrence_days is None if empty
            if not recurrence_days:
                recurrence_days = None

            # Validate Organization & Group
            organization = get_object_or_404(Organization, id=org_id)
            group = get_object_or_404(Group, id=group_id, organization=organization)

            # Create GroupEvent
            group_event = GroupEvent.objects.create(
                organization=organization,
                group=group,
                created_by=request.user,
                title=title,
                description=description,
                date=date,
                start_time=start_time,
                end_time=end_time,
                meeting_link=meeting_link,
                location=location,
                slots=slots,
                recurrence_type=recurrence_type,
                recurrence_end_date=recurrence_end_date,
                recurrence_days=recurrence_days
            )

            return JsonResponse({"success": "Group event created successfully!", "event_id": group_event.id})
        
        except ValidationError as e:
            return JsonResponse({"error": str(e)}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=405)


# Fetch Events and Bookings
def get_profile_picture(user, org_id):
    profile = Profile.objects.filter(user=user, organization_id=org_id).first()
    return profile.profile_picture.url if profile and profile.profile_picture else None

@login_required
def fetch_group_events_new(request):
    org_id = request.GET.get("org_id")
    group_id = request.GET.get("group_id")

    if not org_id or not group_id:
        return JsonResponse({"error": "Missing organization or group ID."}, status=400)

    events = GroupEvent.objects.filter(organization_id=org_id, group_id=group_id).values(
        "id", "title", "date", "start_time", "end_time", "location", "meeting_link"
    )

    return JsonResponse({"events": list(events)})

@login_required
def fetch_event_bookings_new(request):
    org_id = request.GET.get("org_id")
    event_id = request.GET.get("event_id")

    if not org_id or not event_id:
        return JsonResponse({"error": "Missing organization or event ID."}, status=400)

    bookings = GroupEventBooking.objects.filter(
        group_event_id=event_id, organization_id=org_id
    ).select_related("user")

    booking_data = [
        {
            "user_id": booking.user.id,
            "full_name": booking.user.username,
            "profile_picture": get_profile_picture(booking.user, org_id),
            "booking_date": booking.booking_date,
            "booking_time": booking.booking_time,
            "status": booking.status,
        }
        for booking in bookings
    ]

    return JsonResponse({"bookings": booking_data})


# Invite Members into the group (Updated Ajax)
@login_required
def invite_members_to_group_update(request, org_id, group_id):
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    try:
        organization = get_object_or_404(Organization, id=org_id)
        group = get_object_or_404(Group, id=group_id, organization=organization)
        profile = get_object_or_404(Profile, user=request.user, organization=organization)
        
        is_admin = profile.is_admin
        is_team_leader = group.team_leader == request.user
        
        if not (is_admin or is_team_leader):
            return JsonResponse({'error': 'Unauthorized access'}, status=403)
        
        if request.method == 'POST':
            emails = request.POST.get('emails', '').split(',')
            response_data = {'sent': [], 'warnings': [], 'errors': []}
            
            for email in emails:
                email = email.strip()
                try:
                    user = User.objects.get(email=email)
                    if not Profile.objects.filter(user=user, organization=organization).exists():
                        raise ValidationError(f"Email {email} does not belong to an organization member.")
                except User.DoesNotExist:
                    response_data['errors'].append(f"No user found with email: {email}")
                    continue
                except ValidationError as e:
                    response_data['errors'].append(str(e))
                    continue

                if GroupInvitation.objects.filter(recipient_email=email, group=group).exists():
                    response_data['warnings'].append(f"An invitation to {email} has already been sent.")
                else:
                    invitation = GroupInvitation.objects.create(
                        group=group,
                        sender=request.user,
                        recipient_email=email
                    )
                    GroupActivity.objects.create(
                        organization=group.organization,
                        group=group,
                        user=invitation.sender,
                        action_type='INVITED_MEMBER',
                        details=f"{invitation.sender} invited {invitation.recipient_email} in group {group.name}"
                    )
                    
                    invite_link = request.build_absolute_uri(
                        f'/groups/invite/{org_id}/{group_id}/{invitation.id}/accept/'
                    )
                    send_mail(
                        subject=f"Invitation to join {group.name}",
                        message=f"Hello! You are invited to join the group {group.name}. Click the link to accept or reject the invitation:\n{invite_link}",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[email],
                    )
                    response_data['sent'].append(f"Invitation sent to {email}.")
            
            return JsonResponse(response_data)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# Get Invitation status
@login_required
def invitation_status_update(request, org_id, group_id):
    try:
        # Fetch the organization and group
        group = Group.objects.get(id=group_id, organization_id=org_id)
        organization = group.organization

        # Restrict access: user should be part of the organization
        if not Profile.objects.filter(user=request.user, organization=organization).exists():
            return JsonResponse({'error': 'Unauthorized Access'}, status=403)

        # Fetch all invitations for the group
        invitations = GroupInvitation.objects.filter(group=group)

        # Prepare a list of invitation details with user profile picture
        invitation_details = []
        for invitation in invitations:
            profile = Profile.objects.filter(user=invitation.invited_user).first()
            invitation_details.append({
                'recipient_email': invitation.recipient_email,
                'status': invitation.invitation_status,
                'invitation_sent_at': invitation.invitation_sent_at,
                'profile_picture': profile.profile_picture.url if profile and profile.profile_picture else None
            })

        return JsonResponse({'invitations': invitation_details})

    except Group.DoesNotExist:
        return JsonResponse({'error': 'Group not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    

# Task Analytics & Overview
from django.db.models import Count, Avg, Sum, Q, F
import os
from datetime import timedelta
from group_tasks.models import TaskTimeTracking

def get_total_attachment_size(tasks):
    """Helper function to calculate total size of all task attachments."""
    total_size = 0
    for task in tasks:
        if task.attachments:  # Assuming attachments is a FileField or ManyToMany
            attachment_path = os.path.join(settings.MEDIA_ROOT, str(task.attachments))
            if os.path.exists(attachment_path):
                total_size += os.path.getsize(attachment_path)
    return total_size

@login_required
def task_analytics_view_updated(request, org_id, group_id):
    # Fetch Organization and Group Securely
    organization = get_object_or_404(Organization, id=org_id)
    group = get_object_or_404(Group, id=group_id, organization=organization)

    # Ensure User Has Access
    try:
        profile = Profile.objects.get(user=request.user, organization=organization)
        is_admin = profile.is_admin
        is_team_leader = group.team_leader == request.user
        if not (is_admin or is_team_leader):
            return JsonResponse({'error': 'Permission Denied'}, status=403)
    except Profile.DoesNotExist:
        return JsonResponse({'error': 'Unauthorized Access'}, status=403)

    # Query: Fetch all tasks for this group
    tasks = Task.objects.filter(group=group)

    # Total Tasks Count
    total_tasks = tasks.count()

    # Task Status Counts (Pending, In Progress, Completed, etc.)
    task_status_counts = tasks.values('status').annotate(count=Count('status'))
    task_status = {status['status']: status['count'] for status in task_status_counts}

    # Task Progress Analytics
    task_progress = tasks.aggregate(
        avg_progress=Avg('progress', default=0),
        total_progress=Sum('progress', default=0)
    )

    # Fetch Assigned Users
    assigned_users = Profile.objects.filter(
        user__in=tasks.values_list('assigned_to', flat=True),
        organization=organization
    ).values('user__username', 'profile_picture')

    # Get Total Storage Used
    total_storage_used = get_total_attachment_size(tasks)

    # Time Calculations
    total_estimated_time = tasks.aggregate(
        total_estimated=Sum('estimated_completion_time', default=timedelta())
    )['total_estimated']

    total_actual_time = TaskTimeTracking.objects.filter(task__in=tasks).aggregate(
        total_tracked=Sum('time_spent', default=0)
    )['total_tracked']


    
    # Convert Timedelta to Seconds
    estimated_seconds = total_estimated_time.total_seconds() if total_estimated_time else 0
    actual_seconds = float(total_actual_time) * 3600 if total_actual_time else 0


    # Return JSON Response with All Data
    return JsonResponse({
        'total_tasks': total_tasks,
        'task_status': task_status,
        'task_progress': {
            'average_progress': round(task_progress['avg_progress'], 2) if task_progress['avg_progress'] else 0,
            'total_progress': task_progress['total_progress'],
        },
        'assigned_users': list(assigned_users),
        'total_storage_used': total_storage_used,  # Now correctly calculated using OS
        'total_estimated_time': estimated_seconds,
        'total_actual_time': actual_seconds,
    })