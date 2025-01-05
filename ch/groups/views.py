from django.shortcuts import render, redirect , get_object_or_404
from django.urls import reverse
from .models import Group, GroupMember, GroupInvitation, GroupEvent, GroupEventBooking, GroupEventReminder
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
        # Fetch org_id from URL and validate
        self.org_id = kwargs.get('org_id')
        self.organization = get_object_or_404(Organization, id=self.org_id)

        # Ensure the current user is an admin of the organization
        profile = Profile.objects.filter(user=request.user, organization=self.organization, is_admin=True).first()
        if not profile:
            raise PermissionDenied("You are not authorized to create groups for this organization.")

        return super().dispatch(request, *args, **kwargs)

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):
        # Extract form data
        data = {form_name: form.cleaned_data for form_name, form in zip(self.get_form_list().keys(), form_list)}
        name = data['name']['name']
        description = data['description']['description']
        email = data['team_leader']['email']

        # Validate team leader email
        team_leader_profile = Profile.objects.filter(
            user__email=email, organization=self.organization
        ).first()
        if not team_leader_profile:
            form = self.get_form('team_leader')
            form.add_error('email', "The email does not belong to any member of this organization.")
            return self.render_revalidation_failure({'team_leader': form})

        # Create the group
        group = Group.objects.create(
            organization=self.organization,
            name=name,
            description=description,
            team_leader=team_leader_profile.user,
            created_by=self.request.user
        )

        return redirect('display_groups/',org_id=self.org_id)
    



# Display the groups to the admin
class GroupListView(ListView):
    model = Group
    template_name = 'groups/display_groups.html'
    context_object_name = 'groups'
    
    def get_queryset(self):
        org_id = self.kwargs.get('org_id')
        
        # Get the organization based on the org_id
        organization = get_object_or_404(Organization, id=org_id)
        
        # Check if the request.user is an admin of the organization
        if not self.request.user.profiles.filter(organization=organization, is_admin=True).exists():
            raise Http404("You are not an admin of this organization.")

        # Filter groups by the organization and the user who created them
        return Group.objects.filter(organization=organization, created_by=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        org_id = self.kwargs.get('org_id')
        
        # Get the organization to pass it to the template
        organization = get_object_or_404(Organization, id=org_id)
        context['organization'] = organization
        
        return context





# Invite members into the group!
@login_required
def invite_members_to_group(request, org_id, group_id):
    try:
        # Fetch organization and group objects
        organization = Organization.objects.get(id=org_id)
        group = Group.objects.get(id=group_id, organization=organization)

        # Check if the request.user is either:
        # 1. An admin of the organization
        # 2. A team leader of the group
        profile = Profile.objects.get(user=request.user, organization=organization)
        is_admin = profile.is_admin
        is_team_leader = group.team_leader == request.user

        if not (is_admin or is_team_leader):
            raise PermissionDenied

    except (Organization.DoesNotExist, Group.DoesNotExist, Profile.DoesNotExist):
        return HttpResponse("Organization or Group not found.", status=404)

    if request.method == 'POST':
        emails = request.POST.get('emails')
        email_list = emails.split(',')  # Assuming emails are comma-separated
        
        # Check if emails belong to the admin's organization
        for email in email_list:
            email = email.strip()
            try:
                # Check if user with this email exists in the same organization
                user = User.objects.get(email=email)
                if not Profile.objects.filter(user=user, organization=organization).exists():
                    raise ValidationError(f"Email {email} does not belong to an organization member.")
            except User.DoesNotExist:
                raise ValidationError(f"No user found with email: {email}")

            # Send invitation only if the email is valid and not already sent
            if not GroupInvitation.objects.filter(recipient_email=email, group=group).exists():
                invitation = GroupInvitation.objects.create(
                    group=group,
                    sender=request.user,
                    recipient_email=email
                )

                # Send invitation email with a unique URL to accept or reject the invitation
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

    # Check if the invitation is for the correct organization
    if invitation.group.organization.id != org_id:
        messages.error(request, "Invalid invitation link.")
        return redirect('home')

    # Check if the user belongs to the organization of the inviter (admin's organization)
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
                invitation.invitation_status = 'accepted'
                invitation.invited_user = request.user
                invitation.organization=organization
                invitation.save()
                messages.success(request, f"You have successfully joined {invitation.group.name}.")
            else:
                messages.warning(request, "You are already a member of this group.")

        elif action == 'reject':
            # Reject the invitation
            invitation.invitation_status = 'rejected'
            invitation.save()
            messages.success(request, "You have rejected the invitation.")

# redirection is pending!!
        return redirect('home')

    return render(request, 'groups/accept_reject_invitation.html', {'invitation': invitation})



# ------------------------------------------------------------------------------------------------------------------------------------------------------


# Mebers side features for groups and actions

# display the groups
@login_required
def user_groups(request, org_id):
    # Fetch the organization object
    organization = get_object_or_404(Organization, id=org_id)
    
    # Check if the logged-in user is part of the organization
    if not organization.profiles.filter(user=request.user).exists():
        # If the user isn't part of the organization, redirect them or show a message
        return redirect('home')  # Or a custom page with an error message
    
    # Fetch the groups where the user is a member
    user_groups = Group.objects.filter(organization=organization, members__user=request.user)
    
    # Check if the user is the team leader of any group
    team_leader_groups = user_groups.filter(team_leader=request.user)

    return render(request, 'user_groups/user_groups.html', {
        'organization': organization,
        'user_groups': user_groups,
        'team_leader_groups': team_leader_groups,  # Groups where the user is the team leader
    })



# Team Leader

@login_required
def manage_group_users(request, org_id, group_id):
    # Fetch the organization and group objects
    organization = get_object_or_404(Organization, id=org_id)
    group = get_object_or_404(Group, id=group_id, organization=organization)

    # Check if the logged-in user is the team leader
    if group.team_leader != request.user:
        return redirect('user_groups', org_id=org_id)  # Redirect if not team leader

    # Fetch the members of the group
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
    # Fetch the organization, group, and user to be removed
    organization = get_object_or_404(Organization, id=org_id)
    group = get_object_or_404(Group, id=group_id, organization=organization)
    user_to_remove = get_object_or_404(User, id=user_id)

    # Check if the request.user is the team leader of the group
    if group.team_leader != request.user:
        return HttpResponseForbidden("You are not authorized to remove members from this group.")

    # Check if the user to be removed is part of the group
    try:
        group_member = GroupMember.objects.get(group=group, user=user_to_remove)
    except GroupMember.DoesNotExist:
        return redirect('user_groups', org_id=org_id)  # User is not part of the group

    # Remove the user from the group by deleting the membership
    group_member.delete()

    # Redirect back to the group page with a success message
    return redirect('manage_group_users', org_id=org_id , group_id=group.id)



# Team leader Event Creation
@login_required
def create_group_event(request, org_id, group_id):
    # Fetch organization and group
    organization = get_object_or_404(Organization, id=org_id)
    group = get_object_or_404(Group, id=group_id, organization=organization)

    # Check if the user is the team leader
    if group.team_leader != request.user:
        return HttpResponseForbidden("You do not have permission to create events for this group.")
    
    # Handle event creation
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        date = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        meeting_link = request.POST.get('meeting_link')
        location = request.POST.get('location')
        slots = request.POST.get('slots')

        # Validate required fields
        if not title or not date or not start_time or not end_time or not location:
            messages.error(request, "Please fill in all required fields.")
            return redirect('create_group_event', org_id=org_id, group_id=group_id)

        # Create Group Event
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

        # Fetch all group members using GroupMember model
        group_members = GroupMember.objects.filter(group=group)
        
        # Prepare email content
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

        # Send email to each group member
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
    # Fetch organization and group
    organization = get_object_or_404(Organization, id=org_id)
    group = get_object_or_404(Group, id=group_id, organization=organization)

    # Check if the user belongs to the organization and group
    if not GroupMember.objects.filter(group=group, organization=organization, user=request.user).exists():
        return HttpResponseForbidden("You do not have permission to view events for this group.")

    # Fetch all events for this group, ordered by most recent
    events = GroupEvent.objects.filter(group=group).order_by('-created_at')

    # Check if the user has already booked the event using query filtering
    for event in events:
        event.is_booked_by_user = GroupEventBooking.objects.filter(group_event=event, user=request.user).exists()

    return render(request, 'group_events/display_events.html', {
        'organization': organization,
        'group': group,
        'events': events,
    })





# Make Ajax call to book the event
from django.utils.timezone import now, make_aware
from django.utils.html import format_html
from .models import AbsentEvent
from django.utils import timezone

@login_required
@transaction.atomic
def book_group_event(request, org_id, group_id, event_id):
    # Fetch organization, group, and event
    organization = get_object_or_404(Organization, id=org_id)
    group = get_object_or_404(Group, id=group_id, organization=organization)
    event = get_object_or_404(GroupEvent, id=event_id, group=group, organization=organization)

    # Check if the user is part of the group and organization
    if not GroupMember.objects.filter(group=group, organization=organization, user=request.user).exists():
        return HttpResponseForbidden("You are not authorized to book this event.")

    # Get current time (timezone-aware)
    current_time = now()

    # Combine the event date and start time to form a datetime object
    event_datetime = datetime.combine(event.date, event.start_time)
    
    # Make event_datetime timezone-aware
    event_datetime = make_aware(event_datetime, timezone=current_time.tzinfo)

    # Check if the event date and time are valid (future event)
    if event_datetime <= current_time:
        return JsonResponse({"error": "This event is no longer available for booking."}, status=400)

    # Check for existing booking for this user
    if GroupEventBooking.objects.filter(group_event=event, user=request.user).exists():
        return JsonResponse({"error": "You have already booked this event."}, status=400)

    # Check if the event has available slots
    total_bookings = GroupEventBooking.objects.filter(group_event=event).count()
    if total_bookings >= event.slots:
        return JsonResponse({"error": "No slots are available for this event."}, status=400)

    # Create the booking
    booking = GroupEventBooking.objects.create(
        group_event=event,
        organization=organization,
        group=group,
        user=request.user,
        booking_date=current_time.date(),
        booking_time=current_time.time(),
        status='pending',
    )

    # Prepare email content
    user_email = request.user.email
    event_creator_email = event.created_by.email

    subject = f"Event Booking Confirmation: {event.title}"

    # Email body for the user who booked the event
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

    # Email body for the event creator
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

    # Send email to the user who booked the event
    send_mail(
        subject,
        '',
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
        fail_silently=False,
        html_message=user_email_body
    )

    # Send email to the event creator
    send_mail(
        subject,
        '',
        settings.DEFAULT_FROM_EMAIL,
        [event_creator_email],
        fail_silently=False,
        html_message=creator_email_body
    )

    # Respond with success
    return JsonResponse({
        "message": "Event successfully booked and emails sent!",
        "booking_id": booking.id,
        "status": booking.status,
    }, status=201)


# Absent Event
@login_required
def mark_absent(request, org_id, group_id, event_id):
    # Fetch the organization, group, and event
    organization = get_object_or_404(Organization, id=org_id)
    group = get_object_or_404(Group, id=group_id, organization=organization)
    event = get_object_or_404(GroupEvent, id=event_id, group=group, organization=organization)

    # Check if the user is a member of the group and the organization
    if not GroupMember.objects.filter(group=group, organization=organization, user=request.user).exists():
        return JsonResponse({"error": "You are not a member of this group or organization."}, status=400)

     # Prevent marking absent for the same event multiple times
    if AbsentEvent.objects.filter(event=event, user=request.user).exists():
        return JsonResponse({"error": "As per organization rules you can only be absent to one event not more than one!."}, status=400)
    
    # Handle POST request to mark absence
    if request.method == 'POST':
        # Ensure the user has selected a reason
        reason = request.POST.get('reason')
        custom_message = request.POST.get('custom_message')

        # Validate the reason
        if not reason:
            return JsonResponse({"error": "Invalid reason selected."}, status=400)

        # Create a new absence record
        absent_event = AbsentEvent.objects.create(
            organization=organization,
            event=event,
            group=group,
            user=request.user,
            reason=reason,
            custom_message=custom_message,
            date=timezone.now(),
        )

        # Return success response
        return JsonResponse({
            "message": f"You have marked yourself as absent for the event: {event.title}.",
            "absent_event_id": absent_event.id
        }, status=201)

    return JsonResponse({"error": "Invalid request method."}, status=405)



# Handle Reminders
@login_required
def set_event_reminder(request, org_id, group_id, event_id):
    # Fetch the organization, group, and event
    organization = get_object_or_404(Organization, id=org_id)
    group = get_object_or_404(Group, id=group_id, organization=organization)
    event = get_object_or_404(GroupEvent, id=event_id, group=group, organization=organization)

    # Check if the user is a member of the group and organization
    if not GroupMember.objects.filter(group=group, organization=organization, user=request.user).exists():
        return JsonResponse({"error": "You are not a member of this group or organization."}, status=400)

    # Prevent setting multiple reminders for the same event by the same user
    existing_reminder = GroupEventReminder.objects.filter(event=event, group=group, organization=organization, user=request.user).first()
    if existing_reminder:
        return JsonResponse({"error": "You have already set a reminder for this event."}, status=400)

    # Handle POST request to create a new reminder
    if request.method == 'POST':
        # Get reminder options from POST data
        reminder_option = request.POST.get('reminder_option')
        custom_time = request.POST.get('custom_time')  # this will be in datetime format
        reason = request.POST.get('reason')

        # Validate the reminder option
        if reminder_option not in ['1_day_before', '1_hour_before', 'custom']:
            return JsonResponse({"error": "Invalid reminder option."}, status=400)

        # Handle custom reminder time
        if reminder_option == 'custom' and not custom_time:
            return JsonResponse({"error": "Custom time is required for custom reminder."}, status=400)

        if reminder_option == 'custom':
            try:
                custom_time = timezone.make_aware(timezone.datetime.strptime(custom_time, '%Y-%m-%d %H:%M:%S'))
            except ValueError:
                return JsonResponse({"error": "Invalid custom time format. Please use 'YYYY-MM-DD HH:MM:SS'."}, status=400)

        # Create the reminder
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

            # Return success response
            return JsonResponse({
                "message": f"Reminder set successfully for event: {event.title}.",
                "reminder_id": reminder.id
            }, status=201)

        except IntegrityError:
            return JsonResponse({"error": "Failed to create reminder. Please try again."}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=405)