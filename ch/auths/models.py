from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
import secrets
from datetime import datetime, timedelta


class Organization(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_organizations')

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profiles')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='profiles')
    is_admin = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)
    is_employee = models.BooleanField(default=False)  # Default to False for control

    def __str__(self):
        return f"{self.user.username} - {self.organization.name} ({'Admin' if self.is_admin else 'Manager' if self.is_manager else 'Employee'})"

    def save(self, *args, **kwargs):
     
        if self.is_admin and Profile.objects.filter(organization=self.organization, is_admin=True).exists():
            raise ValueError("An organization can have only one admin.")
        super().save(*args, **kwargs)


# invitation model

class Invitation(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )

    ROLE_CHOICES = (
        ('manager', 'Manager'),
        ('employee', 'Employee'),
    )

    inviter = models.ForeignKey(User, related_name='sent_invitations', on_delete=models.CASCADE)
    invitee = models.ForeignKey(User, related_name='received_invitations', on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, related_name='invitations', on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    expires_at = models.DateTimeField()

    def is_valid(self):
        """ Check if the invitation is still valid (i.e., not expired) """
        return timezone.now() < self.expires_at

    def accept_invitation(self):
      """Accept the invitation and add the user to the organization."""
      if self.status != 'pending' or not self.is_valid():
          return False
      
      inviter_profile = Profile.objects.filter(user=self.inviter, organization=self.organization).first()
      if not inviter_profile:
         raise ValueError("Inviter does not have a valid profile for this organization.")

      is_manager = self.role == 'manager'
      is_employee = self.role == 'employee'

      Profile.objects.create(
        user=self.invitee,
        organization=self.organization,
        is_admin=False,  
        is_manager=is_manager,
        is_employee=is_employee,
    )

      self.status = 'accepted'
      self.save()
      return True

    def reject_invitation(self):
        """ Reject the invitation """
        if self.status == 'pending':
            self.status = 'rejected'
            self.save()
            return True
        return False

# invite by email 

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
        """Accept the invitation and create a Profile for the user."""
        if self.status != 'pending' or not self.is_valid():
            return False
        Profile.objects.create(
            user=user,
            organization=self.organization,
            is_admin=(self.role == 'manager'),
            is_manager=(self.role == 'manager'),
            is_employee=(self.role == 'employee')
        )
        self.status = 'accepted'
        self.save()
        return True

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






# calendar +
class Availability(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="availabilities")
    day_of_week = models.CharField(max_length=10, choices=[
        ("Monday", "Monday"),
        ("Tuesday", "Tuesday"),
        ("Wednesday", "Wednesday"),
        ("Thursday", "Thursday"),
        ("Friday", "Friday"),
        ("Saturday", "Saturday"),
        ("Sunday", "Sunday"),
    ],null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    meeting_duration = models.PositiveIntegerField(null=True, blank=True)  # Duration of the meeting in minutes
    buffer_time = models.PositiveIntegerField(null=True, blank=True)  # Buffer time between meetings in minutes
    is_recurring = models.BooleanField(default=False,null=True, blank=True)  # Recurring availability (can be used for recurring events)
    is_booked = models.BooleanField(default=False,null=True, blank=True) 

    def __str__(self):
        return f"{self.user.username} - {self.day_of_week}: {self.start_time} to {self.end_time}"
    

   
# MEETING MODEL 


# model for meeting
class Meets(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE,related_name="created_meetings",blank=True, null=True)  # The person scheduling the meeting (you)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="meetings")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    day_of_week = models.CharField(max_length=10)
    start_time = models.TimeField()
    end_time = models.TimeField()
    participants = models.ManyToManyField(User, related_name='meetings_participants',null=True, blank=True)
    # is_booked = models.BooleanField(default=False, null=True, blank=True)

    def __str__(self):
        return f"{self.title} with {self.user.username} (Created by {self.creator}) on {self.day_of_week}"
    

    
# model for custom reminders

class Reminder(models.Model):
    meeting = models.ForeignKey('Meets', on_delete=models.CASCADE, related_name='reminders')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reminders')
    reminder_time = models.DateTimeField()
    created_at= models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Reminder for {self.meeting.title}'
    

    class Meta:
        ordering = ['reminder_time']
        

# model for send meeting invitations
class MeetInvitation(models.Model):
    meeting = models.ForeignKey('Meets', on_delete=models.CASCADE, related_name='invitations')
    invited_users = models.ManyToManyField(User, related_name='meeting_invitations')  # Allows inviting multiple users
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_meeting_invitations')
    status = models.CharField(
        max_length=10,
        choices=[
            ('Pending', 'Pending'),
            ('Accepted', 'Accepted'),
            ('Declined', 'Declined'),
        ],
        default='Pending'
    )
    sent_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Invitation for {self.meeting.title} by {self.invited_by.username} (Status: {self.status})"

    def accept_invitation(self, user):
        """Accept the invitation for a specific user."""
        if user not in self.invited_users.all():
            raise ValueError(f"{user.username} was not invited to this meeting.")

        if self.status == 'Pending':
            self.status = 'Accepted'
            self.responded_at = timezone.now()
            self.meeting.participants.add(user)  # Add user to the meeting participants
            self.save()
            return True
        return False

    def reject_invitation(self, user):
        """Reject the invitation for a specific user."""
        if user not in self.invited_users.all():
            raise ValueError(f"{user.username} was not invited to this meeting.")

        if self.status == 'Pending':
            self.status = 'Declined'
            self.responded_at = timezone.now()
            self.save()
            return True
        return False



# contact list


class Contacts(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contacts')
    contact_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='added_by')
    created_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"{self.user.username} added {self.contact_user.username} to contacts"
    
# add to favourite     

class FavoriteContact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_contacts')
    contact = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'contact')

    def __str__(self):
        return f'{self.contact.username} is a favorite of {self.user.username}'