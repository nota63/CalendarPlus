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
    reminder_message = models.TextField(null=True, blank=True)  # Custom message for the reminder
    # New field for the carryover
    carryover = models.BooleanField(default=False, null=True, blank=True)  # New field for Holiday Carryover
    



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
    meeting_link = models.URLField(blank=True, null=True)  # Link for the online meeting (Zoom, Google Meet, etc.)
    meeting_location = models.CharField(max_length=255, choices=[('zoom', 'Zoom'), ('google_meet', 'Google Meet'), ('zoho', 'Zoho'), ('in_person', 'In-person')], default='in_person')
    meeting_type = models.CharField(max_length=255, choices=[('standup', 'Standup'), ('task', 'Task'), ('project_discussion', 'Project Discussion'), ('other', 'Other')], default='other')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Optional fields like status or notification flags
    status = models.CharField(max_length=50, choices=[('scheduled', 'Scheduled'), ('completed', 'Completed'), ('canceled', 'Canceled')], default='scheduled')
    is_notification_sent = models.BooleanField(default=False)  # Flag to mark if notifications are sent

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
        (0, 'On meeting time')  # Added option for "On meeting time"
    ]
    
    REMINDER_TYPE_CHOICES = [
        ('email', 'Email'),  # User can only select Email
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    meeting = models.ForeignKey(MeetingOrganization, on_delete=models.CASCADE)  # Link reminder to a specific meeting
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # User who sets the reminder

    reminder_type = models.CharField(
        max_length=20,
        choices=REMINDER_TYPE_CHOICES,
        default='email'
    )
    
    # Reminder time options: 15, 30, 45 minutes before or on meeting time
    reminder_time = models.IntegerField(
        choices=REMINDER_TIME_CHOICES,
        default=15
    )

    # Custom time input (minutes or hours) for other reminder options
    custom_minutes = models.IntegerField(null=True, blank=True)
    custom_hours = models.IntegerField(null=True, blank=True)

    # Store the calculated reminder time (datetime)
    reminder_datetime = models.DateTimeField(null=True, blank=True)

    # New field to determine whether to remind all members
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
    default='minimalist',  # Default style
    help_text="Choose a theme for your reminder email template."
   , null=True , blank=True)

    def __str__(self):
        return f"Reminder for {self.meeting.meeting_title} ({self.reminder_type})"
    
    def save(self, *args, **kwargs):
        # Calculate the reminder time based on user input
        if self.reminder_time == 0:  # On meeting time
            # Set reminder exactly at the meeting time (no offset)
            reminder_offset = timedelta(minutes=0)
        elif self.reminder_time == 15 or self.reminder_time == 30 or self.reminder_time == 45:  # Predefined times
            reminder_offset = timedelta(minutes=self.reminder_time)
        else:  # Custom time handling
            if self.custom_minutes:
                reminder_offset = timedelta(minutes=self.custom_minutes)
            elif self.custom_hours:
                reminder_offset = timedelta(hours=self.custom_hours)
            else:
                reminder_offset = timedelta(minutes=15)  # Default to 15 minutes if no input

        # Calculate the reminder datetime (meeting datetime - reminder offset)
        meeting_datetime = datetime.combine(self.meeting.meeting_date, self.meeting.start_time)
        self.reminder_datetime = meeting_datetime - reminder_offset
        
        super().save(*args, **kwargs)