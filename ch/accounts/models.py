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




class OngoingMeetings(models.Model):
    user= models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    meeting_schedules= models.JSONField(null=True)







# Availability model 


# calendar +
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

    class Meta:
        unique_together = ('user', 'organization', 'day_of_week', 'start_time', 'end_time')