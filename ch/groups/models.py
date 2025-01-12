from django.db import models
from accounts.models import Organization, Profile
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

# Create a Group Model 

class Group(models.Model):
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE, 
        related_name='groups'
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    team_leader = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='leading_groups'
    )
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='created_groups'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.organization.name})"


# Group Members

class GroupMember(models.Model):
    group = models.ForeignKey(
        Group, 
        on_delete=models.CASCADE, 
        related_name='members'
    )
    organization= models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='group_memberships',
        null=True, blank=True
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='group_memberships'
    )
    role = models.CharField(
        max_length=50,
        choices=[
            ('member', 'Member'),
        ],
        default='member'
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('group', 'user')

    def __str__(self):
        return f"{self.user.username} in {self.group.name}"



# Group Invitations

# Group Invitation Model
class GroupInvitation(models.Model):
    organization=models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='grouped_organization', null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='invitations')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invitations')
    recipient_email = models.EmailField() 
    role = models.CharField(max_length=50, choices=[('member', 'Member')], default='member')
    invitation_sent_at = models.DateTimeField(auto_now_add=True)
    invitation_status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')],
        default='pending'
    )
    invited_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='invitations_received')

    def __str__(self):
        return f"Invitation to {self.recipient_email} for {self.group.name}"

    def accept_invitation(self):
        if self.invitation_status == 'pending':
            # Add user to group if accepted
            if not GroupMember.objects.filter(group=self.group, user=self.invited_user).exists():
                group_member = GroupMember(group=self.group, user=self.invited_user, role=self.role)
                group_member.save()
                self.invitation_status = 'accepted'
                self.save()
            else:
                # Handle case where user is already in the group (optional)
                self.invitation_status = 'rejected'  # Reject the invitation
                self.save()

    def reject_invitation(self):
        if self.invitation_status == 'pending':
            self.invitation_status = 'rejected'
            self.save()


# Group Events

class GroupEvent(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='events')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='group_events')  # New field
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    meeting_link=models.URLField()
    location = models.CharField(
    max_length=255,
    choices=(
        ('Zoom', 'Zoom'),
        ('Google Meet', 'Google Meet'),
        ('Organization', 'Organization'),
        ('Salesforce', 'Salesforce'),
        ('Microsoft Teams', 'Microsoft Teams'),
        ('Skype', 'Skype'),
        ('Webex', 'Webex'),
        ('Slack', 'Slack'),
    )
)

    slots = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    recurrence_type = models.CharField(
        max_length=20,
        choices=(
            ('none', 'None'),  
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('bi-weekly', 'Bi-Weekly'),
            ('monthly', 'Monthly'),
            ('yearly', 'Yearly'),
        ),
        default='none', null=True, blank=True
    )
    recurrence_end_date = models.DateField(null=True, blank=True)  
    recurrence_days = models.CharField(
        max_length=50,
        blank=True,
        help_text="Comma-separated days for weekly recurrence, e.g., 'Monday, Wednesday'."
    )


# Group Event Booking
class GroupEventBooking(models.Model):
    group_event = models.ForeignKey(GroupEvent, on_delete=models.CASCADE, related_name='bookings')
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE, 
        related_name='event_bookings'
    )  # Field for organization
    group = models.ForeignKey(
        Group, 
        on_delete=models.CASCADE, 
        related_name='group_event_bookings'
    )  
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    booking_date = models.DateField()
    booking_time = models.TimeField()
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('confirmed', 'Confirmed'),
            ('cancelled', 'Cancelled')
        ],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



# Absent on Event

class AbsentEvent(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE,related_name='absent_organization')
    event=models.ForeignKey(GroupEvent, on_delete=models.CASCADE, related_name='absent_event')
    group=models.ForeignKey(Group, on_delete=models.CASCADE, related_name='absent_group')
    user=models.ForeignKey(User, on_delete=models.CASCADE, related_name='absent_user')
    reason=models.CharField(max_length=100, choices=(('Personal','personal'),('Availability Issues','availability issues'),('Other','other')))
    custom_message = models.TextField()
    date=models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Absent {self.user.username} for event - {self.event.title}'


# Reminder

class GroupEventReminder(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="event_reminders")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="event_reminders")
    event = models.ForeignKey(GroupEvent, on_delete=models.CASCADE, related_name="reminders")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="event_reminders")
    
    # Reminder options
    reminder_options = models.CharField(
        max_length=20,
        choices=(
            ('1_day_before', '1 Day Before'),
            ('1_hour_before', '1 Hour Before'),
            ('custom', 'Custom Time'),
        ),
        default='1_day_before'
    )
    custom_time = models.DateTimeField(null=True, blank=True)  # Only used if 'custom' is selected
    
    reminder_message = models.CharField(max_length=255, blank=True, null=True)
    is_sent = models.BooleanField(default=False)
    
    
    reason = models.CharField(max_length=255, choices=(
        ('Upcoming', 'Upcoming Event'),
        ('Custom', 'Custom Reminder'),
    ), default='Upcoming')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Reminder for {self.user.username} about event {self.event.title} ({self.reminder_options})"
    
    class Meta:
        unique_together = ('organization', 'group', 'event', 'user', 'reminder_options', 'custom_time')



# Model to track the group activity

class GroupActivity(models.Model):
    ACTION_CHOICES = [
        ('ADD_MEMBER', 'Added member'),
        ('REMOVE_MEMBER', 'Removed member'),
        ('CREATE_TASK', 'Created task'),
        ('UPDATE_TASK', 'Updated task'),
        ('DELETE_TASK', 'Deleted task'),
        ('GROUP_CREATED', 'Created group'),
        ('GROUP_UPDATED', 'Updated group'),
        ('GROUP_DELETED', 'Deleted group'),
        ('INVITE_MEMBER', 'Invited member'),
        ("INVITATION_ACCEPT",'Invitation accepted'),
        ('INVITATION_REJECT','Invitation rejected'),
        ('MEMBER_DISCARD','Member removed'),
        ("CREATE_EVENT",'Event created'),
        ("BOOK_EVENT",'Event booked'),
        ("MARK_ABSENT",'Marked as absent'),
        ("SET_EVENT_REMINDER",'Reminder set'),
        ("DELETE_EVENT",'Event deleted'),
        ('RECURRING_EVENT','Set event as recurring')
        
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    event=models.ForeignKey(GroupEvent, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=50, choices=ACTION_CHOICES)
    details = models.TextField(blank=True, null=True) 
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.get_action_type_display()} on {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']

