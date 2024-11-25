from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
import secrets


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


