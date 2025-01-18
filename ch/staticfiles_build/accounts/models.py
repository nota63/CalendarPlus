from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
import secrets
from datetime import datetime, timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
import uuid
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings
from tinymce.models import HTMLField


# Models 
# organization model 
class Organization(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_organizations')
 
   

    def __str__(self):
        return self.name

# profile
class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profiles')
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, related_name='profiles', null=True, blank=True)
    is_admin = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)
    is_employee = models.BooleanField(default=False)  
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)  
    full_name = models.CharField(max_length=255, null=True, blank=True)  

    class Meta:
        unique_together = ('user', 'organization') 
    def __str__(self):
        return f"{self.user} - {self.organization} ({'Admin' if self.is_admin else 'Manager' if self.is_manager else 'Employee'})"
    
    def save(self, *args, **kwargs):
     print(f"Saving profile: {self}, is_admin={self.is_admin}, organization={self.organization}")
    
     if self.is_admin:
        if Profile.objects.filter(organization=self.organization, is_admin=True).exclude(id=self.id).exists():
            raise ValueError("An organization can have only one admin.")
     super().save(*args, **kwargs)



# project model 
class Project(models.Model):
    name = models.CharField(max_length=255)  # Project name
    description = models.TextField(blank=True, null=True) 
    start_date = models.DateField(null=True, blank=True) 
    end_date = models.DateField(null=True, blank=True) 
    organization = models.ForeignKey(
        'Organization',
        on_delete=models.CASCADE,
        related_name='projects'
    )  
    created_by = models.ForeignKey(
        'Profile',  
        on_delete=models.CASCADE,
        related_name='created_projects'
    )  
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)  

    def __str__(self):
        return self.name

# Model to assign managers to projects
class ProjectManagerAssignment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE,related_name='projects_assignments')
    manager = models.ForeignKey(Profile, on_delete=models.CASCADE, limit_choices_to={'is_manager': True})
    assigned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.manager} assigned to {self.project}"

# Model to assign employees to managers (employees are assigned to a manager within a project)
class ProjectEmployeeAssignment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    employee = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        limit_choices_to={'is_employee': True},
        related_name='employee_assignments' 
    )
    manager = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        limit_choices_to={'is_manager': True},
        related_name='manager_assignments'  
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee} assigned to {self.manager} for {self.project}"

        
class EmailInvitation(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )

    ROLE_CHOICES = (
        ('manager', 'Manager'),
        ('employee', 'Employee'),
    )

    inviter = models.ForeignKey(User, related_name='email_sent_invitations', on_delete=models.CASCADE)
    invitee_email = models.EmailField()  
    organization = models.ForeignKey(Organization, related_name='email_invitations', on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    token = models.CharField(max_length=64, unique=True) 
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    expires_at = models.DateTimeField()

    def is_valid(self):
        """Check if the invitation is still valid."""
        return timezone.now() < self.expires_at

   
    
    def accept_invitation(self, user):
        # Ensure the organization exists
        if not self.organization:
            raise ValueError("Invalid organization in invitation.")

        # Map invitation roles to profile attributes
        is_admin = self.role == 'admin'
        is_manager = self.role == 'manager'
        is_employee = self.role == 'employee'

      
        profile, created = Profile.objects.get_or_create(
            user=user,
            organization=self.organization,
            defaults={
                'is_admin': is_admin,
                'is_manager': is_manager,
                'is_employee': is_employee,
            }
        )

   
        if not created:
            profile.is_admin = is_admin
            profile.is_manager = is_manager
            profile.is_employee = is_employee
            profile.save()

      
        self.accepted = True
        self.save()


    def reject_invitation(self):
        """Reject the invitation."""
        if self.status == 'pending':
            self.status = 'rejected'
            self.save()
            return True
        return False

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(32)  
        super().save(*args, **kwargs)





# Availability model 
class Availability(models.Model):
    DAYS_OF_WEEK = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='availabilities', null=True, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='availabilities', null=True, blank=True)
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK, null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    is_booked=models.BooleanField(default=False, null=True, blank=True)

    class Meta:
        unique_together = ('user', 'organization', 'day_of_week', 'start_time', 'end_time')

    def __str__(self):
        return f'{self.day_of_week} - {self.start_time} - {self.end_time}'
    

# Holidays 

class HolidayOrganization(models.Model):
    organization = models.ForeignKey(Organization, related_name='holidaysorg', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='holidaysorg', on_delete=models.CASCADE)  
    name = models.CharField(max_length=255)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    message_for_invitees=models.TextField(null=True, blank=True)
    # settings fields
   

    def __str__(self):
        return f"{self.name} ({self.start_date} - {self.end_date})"

    class Meta:
        unique_together = ('organization', 'start_date', 'end_date') 


# Holiday settings         

# Holiday Type 
class HolidayType(models.Model):
    name = models.CharField(max_length=255, unique=True)
    
    def __str__(self):
        return self.name


# Holiday Settings
class HolidaySettings(models.Model):
    holiday = models.OneToOneField(HolidayOrganization, on_delete=models.CASCADE, related_name='settings')
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE, related_name='holiday_settings')
    allow_scheduling = models.BooleanField(default=False)
    holiday_visibility = models.BooleanField(default=True)
    is_recurring = models.BooleanField(default=False, null=True, blank=True)
    holiday_type = models.ForeignKey(HolidayType, null=True, blank=True, on_delete=models.SET_NULL)
    # New field for Holiday Notifications
    holiday_notifications = models.BooleanField(default=False, null=True, blank=True)

    notify_organization_members = models.BooleanField(default=False, null=True, blank=True)
    reminder_days_before = models.IntegerField(default=0, choices=[(i, i) for i in range(1, 31)], null=True, blank=True)  # Number of days before the holiday to send reminder
    reminder_message = models.TextField(null=True, blank=True) 
    carryover = models.BooleanField(default=False, null=True, blank=True) 
    



    def __str__(self):
        return f"Settings for {self.holiday.name} ({self.organization.name})"
    

# Organization Meetings

class MeetingOrganization(models.Model):
    organization = models.ForeignKey(Organization, related_name="meetingss", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="user_meetingss", on_delete=models.CASCADE, null=True, blank=True)  # The user whose calendar is being viewed
    invitee = models.ForeignKey(User, related_name="created_meetingss", on_delete=models.CASCADE,null=True, blank=True)  # The invitee (the person creating the meeting)
    
    meeting_title = models.CharField(max_length=255)
    meeting_description = models.TextField(blank=True, null=True)
    
    # Scheduling fields
    meeting_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    # New fields
    meeting_link = models.URLField(blank=True, null=True) 
    meeting_location = models.CharField(max_length=255, choices=[('zoom', 'Zoom'), ('google_meet', 'Google Meet'), ('zoho', 'Zoho'), ('in_person', 'In-person')], default='in_person')
    meeting_type = models.CharField(max_length=255, choices=[('standup', 'Standup'), ('task', 'Task'), ('project_discussion', 'Project Discussion'), ('other', 'Other')], default='other')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    status = models.CharField(max_length=50, choices=[('scheduled', 'Scheduled'), ('completed', 'Completed'), ('canceled', 'Canceled')], default='scheduled')
    is_notification_sent = models.BooleanField(default=False) 

    participants= models.ManyToManyField(User, related_name='participants_meetings', null=True, blank=True)

    def __str__(self):
        return f"Meeting: {self.meeting_title} on {self.meeting_date} from {self.start_time} to {self.end_time}"

    class Meta:
        unique_together = ('organization', 'meeting_date', 'start_time', 'user')  # Ensures no double-booking for the same user


# Meeting Reminder
class MeetingReminder(models.Model):
    REMINDER_TIME_CHOICES = [
        (15, '15 minutes before'),
        (30, '30 minutes before'),
        (45, '45 minutes before'),
        (0, 'On meeting time')  
    ]
    
    REMINDER_TYPE_CHOICES = [
        ('email', 'Email'),  
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    meeting = models.ForeignKey(MeetingOrganization, on_delete=models.CASCADE)  
    user = models.ForeignKey(User, on_delete=models.CASCADE)  

    reminder_type = models.CharField(
        max_length=20,
        choices=REMINDER_TYPE_CHOICES,
        default='email'
    )
    
  
    reminder_time = models.IntegerField(
        choices=REMINDER_TIME_CHOICES,
        default=15
    )

    
    custom_minutes = models.IntegerField(null=True, blank=True)
    custom_hours = models.IntegerField(null=True, blank=True)

  
    reminder_datetime = models.DateTimeField(null=True, blank=True)

  
    remind_all_members = models.BooleanField(default=False)
    reminder_style = models.CharField(
    max_length=100,
    choices=[
        ('minimalist', 'Minimalist'),
        ('modern', 'Modern'),
        ('dark', 'Dark'),
        ('classic', 'Classic'),
        ('playful', 'Playful'),
    ],
    default='minimalist',  
    help_text="Choose a theme for your reminder email template."
   , null=True , blank=True)

    def __str__(self):
        return f"Reminder for {self.meeting.meeting_title} ({self.reminder_type})"
    
    def save(self, *args, **kwargs):
        
        if self.reminder_time == 0: 
            reminder_offset = timedelta(minutes=0)
        elif self.reminder_time == 15 or self.reminder_time == 30 or self.reminder_time == 45: 
            reminder_offset = timedelta(minutes=self.reminder_time)
        else:  
            if self.custom_minutes:
                reminder_offset = timedelta(minutes=self.custom_minutes)
            elif self.custom_hours:
                reminder_offset = timedelta(hours=self.custom_hours)
            else:
                reminder_offset = timedelta(minutes=15)  

        meeting_datetime = datetime.combine(self.meeting.meeting_date, self.meeting.start_time)
        self.reminder_datetime = meeting_datetime - reminder_offset
        
        super().save(*args, **kwargs)


# Invite other users in the meeting 
def generate_random_string():
         return get_random_string(50)

class MeetingInvitationOrganization(models.Model):
    meeting = models.ForeignKey('MeetingOrganization', related_name='invitations', on_delete=models.CASCADE)
    invitee = models.ForeignKey(User, related_name='meeting_invitationss', on_delete=models.CASCADE)  # The user invited to the meeting
    organization = models.ForeignKey(Organization, related_name='meeting_invitations', on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined')],
        default='pending'
    )
    invited_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    declined_at = models.DateTimeField(null=True, blank=True)
    
   
    # A unique token for the invite link with the correct length argument
    invite_token = models.CharField(max_length=50, unique=True, default=generate_random_string)
    
    
 
    is_email_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Invite to {self.invitee.username} for meeting {self.meeting.meeting_title} ({self.status})"

    def accept_invite(self):
        """Accept the invitation and mark the status as accepted."""
        self.status = 'accepted'
        self.accepted_at = timezone.now()
        self.save()
    
    def decline_invite(self):
        """Decline the invitation and mark the status as declined."""
        self.status = 'declined'
        self.declined_at = timezone.now()
        self.save()

    def send_invite_email(self):
        """Send an email invite to the invitee."""
        if not self.is_email_sent:
            subject = f"You're invited to the meeting: {self.meeting.meeting_title}"
            message = f"Hello {self.invitee.username},\n\nYou are invited to the meeting '{self.meeting.meeting_title}' on {self.meeting.meeting_date} at {self.meeting.start_time}. To accept the invitation, click the link below:\n\n{self.get_invite_link()}\n\nBest regards,\nYour Organization"
            from_email = settings.DEFAULT_FROM_EMAIL
            
            send_mail(subject, message, from_email, [self.invitee.email])
            self.is_email_sent = True
            self.save()

    def get_invite_link(self):
        """Generate the invite link with the token."""
        return f"{settings.SITE_URL}/org_accept_invite/{self.invite_token}/"
    

# Meeting Agenda 

class Agenda(models.Model):
    organization = models.ForeignKey(
        'Organization',
        on_delete=models.CASCADE,
        related_name='agendas'
    )
    meeting = models.ForeignKey(
        'MeetingOrganization',
        on_delete=models.CASCADE,
        related_name='agendas'
    )
    agenda_content =HTMLField()
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_agendas'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Agenda for {self.meeting.meeting_title} by {self.created_by}"

    class Meta:
        verbose_name = "Meeting Agenda"
        verbose_name_plural = "Meeting Agendas"


# Collaborate on notes
class MeetingNotes(models.Model):
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE)
    meeting = models.ForeignKey('MeetingOrganization', on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)  
    mentions = models.ManyToManyField(User, null=True,blank=True, related_name='mentioned_in_notes')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)  
    class Meta:
        unique_together = ('organization', 'meeting',)

    def __str__(self):
        return f"Notes for {self.meeting.meeting_title} by "
    


# MeetingRoom 
class MeetingRoom(models.Model):
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE)
    meeting = models.ForeignKey('MeetingOrganization', on_delete=models.CASCADE)
    room_name = models.CharField(max_length=255, unique=True)  # Each room has a unique name (combination of org_id and meeting_id)
    participants = models.ManyToManyField(User, related_name='meeting_participants')

    def __str__(self):
        return f"Room for {self.meeting.meeting_title}"
    


# Event Creation


class EventOrganization(models.Model):
    EVENT_TYPES = [
        ('one_on_one', 'One-on-One'),
        ('group', 'Group Meeting'),
    ]
    
    LOCATION_CHOICES = [
        ('Google Meet', 'Google Meet'),
        ('Zoom', 'Zoom'),
        ('Phone Call', 'Phone Call'),
        ('In Person Meeting', 'In Person Meeting'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="eventss", null=True, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="events", null=True, blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, default='one_on_one', null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    duration = models.PositiveIntegerField(null=True, blank=True)
    buffer_time = models.PositiveIntegerField(default=0, null=True, blank=True)
    is_recurring = models.BooleanField(default=False, null=True, blank=True)
    location = models.CharField(
        max_length=100, choices=LOCATION_CHOICES, default='Google Meet', null=True, blank=True
    )
    slug = models.SlugField(unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    

    def save(self, *args, **kwargs):
      if not self.slug:
        # Ensure the title is used to create a slug if it's not empty; otherwise, use just the UUID
        base_slug = self.title if self.title else f"event-{uuid.uuid4().hex[:8]}"
        self.slug = slugify(f"{base_slug}-{uuid.uuid4().hex[:8]}")  # Generate unique slug
      super().save(*args, **kwargs)
   

    def __str__(self):
        return f"{self.title} ({self.user.username})"






class BookingOrganization(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    organization= models.ForeignKey('Organization', on_delete=models.CASCADE, related_name='booking_organization')

    event = models.ForeignKey('EventOrganization', on_delete=models.CASCADE, related_name='bookings')
    invitee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookingss')
    event_host=models.ForeignKey(User,on_delete=models.CASCADE, related_name='event_hosts', blank=True,null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Booking for {self.event.title} by {self.invitee.username} at {self.start_time}"

    def is_accepted(self):
        return self.status == 'confirmed'

    def cancel(self):
        self.status = 'cancelled'
        self.save()

    def confirm(self):
        self.status = 'confirmed'
        self.save()


    












