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
@login_required
def user_groups(request, org_id):
    
    organization = get_object_or_404(Organization, id=org_id)
    

    if not organization.profiles.filter(user=request.user).exists():
    
        return redirect('home')  
    
   
    user_groups = Group.objects.filter(organization=organization, members__user=request.user)
    
    
    team_leader_groups = user_groups.filter(team_leader=request.user)

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

   
    if group.team_leader != request.user:
        return redirect('user_groups', org_id=org_id)  


    members = GroupMember.objects.filter(group=group)

    return render(request, 'user_groups/manage_group_users.html', {
        'organization': organization,
        'group': group,
        'members': members,
    })





# Remove the user from the grop

# team leader can access this view 
from django.http import HttpResponseForbidden
@login_required
def remove_user_from_group(request, org_id, group_id, user_id):
   
    organization = get_object_or_404(Organization, id=org_id)
    group = get_object_or_404(Group, id=group_id, organization=organization)
    user_to_remove = get_object_or_404(User, id=user_id)

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

    if not GroupMember.objects.filter(group=group, organization=organization, user=request.user).exists():
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

def group_member_details(request, org_id, group_id, user_id):
    organization = get_object_or_404(Organization, id=org_id)
    group = get_object_or_404(Group, id=group_id, organization=organization)


    if group.team_leader != request.user:
        raise PermissionDenied("You are not authorized to view this member.")

    
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






