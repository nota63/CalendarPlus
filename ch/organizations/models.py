from django.db import models
from accounts.models import Organization, MeetingOrganization
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.timezone import now
from django.contrib.auth.hashers import make_password, check_password
from django.utils.crypto import get_random_string
from cryptography.fernet import Fernet
import base64
import os
# Create your models here.


# HIDE ORGANIZATION

class OrganizationHide(models.Model):
    from_organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="hidden_by"
    )  
    to_organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="hidden_from"
    )  
    hider = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="hidden_organizations"
    )   
    hidden_from = models.DateTimeField()  
    hidden_until = models.DateTimeField()  
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True)  
    notify_members=models.BooleanField(default=False, null=True, blank=True)
    hide_on_sundays_and_holidays = models.BooleanField(default=False,null=True, blank=True)  


    def is_active(self):
        """Check if the hide is currently active"""
        return self.hidden_from <= timezone.now() <= self.hidden_until  

    def __str__(self):
        return f"{self.to_organization.name} hidden by {self.from_organization.name} (Hider: {self.hider.username})"




# Schedule meetings

class RecurringMeeting(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="recurring_meetings",null=True, blank=True)
  
    type=models.CharField(max_length=100, choices=(('Recurring Meeting','recurring_meeting'),('Urgent','urgent')),default='Urgent',null=True, blank=True)
    
   
    RECURRING_CHOICES = [
        ("daily", "Every Day"),
        ("weekly", "Every Week"),
        ("monthly", "Every Month"),
        ("yearly", "Every Year"),
        ("custom", "Custom"),
    ]
    
    recurrence_type = models.CharField(max_length=10, choices=RECURRING_CHOICES, default="weekly",null=True, blank=True)
    custom_days = models.JSONField(blank=True, null=True, help_text="Store custom recurrence days as a list [1,3,5] for Mon,Wed,Fri")

    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True, help_text="Leave blank for indefinite recurrence")

 
    remind_before = models.IntegerField(default=15, help_text="Minutes before the meeting to send a reminder")
    send_email_reminder = models.BooleanField(default=True, help_text="Should an email reminder be sent?")
    send_push_notification = models.BooleanField(default=True, help_text="Should a push notification be sent?")
    
 
    exclude_dates = models.JSONField(blank=True, null=True, help_text="List of dates to exclude from recurrence")


    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_recurring_meetings")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="recurring_meetings_set")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f" Meeting Created by {self.created_by} - {self.creator}"

    class Meta:
        unique_together = ("recurrence_type", "start_date")

     

# HELP MODEL TO RAISE QUERIES RELATED TO HELP

class Help(models.Model):
    HELP_TYPE_CHOICES = [
        ("BUG", "Bug Report"),
        ("FEATURE", "Feature Request"),
        ("ACCOUNT", "Account Issue"),
        ("BILLING", "Billing Issue"),
        ("GENERAL", "General Query"),
        ("SECURITY", "Security Concern"),
        ("OTHER", "Other"),
    ]

    STATUS_CHOICES = [
        ("OPEN", "Open"),
        ("IN_PROGRESS", "In Progress"),
        ("RESOLVED", "Resolved"),
        ("CLOSED", "Closed"),
    ]

    PRIORITY_CHOICES = [
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High"),
        ("URGENT", "Urgent"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="help_queries")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="help_queries")
    help_type = models.CharField(max_length=20, choices=HELP_TYPE_CHOICES, default="GENERAL")
    title = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="MEDIUM")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="OPEN")
    response = models.TextField(blank=True, null=True)  # Admin response field
    attachment = models.FileField(upload_to="help_attachments/", blank=True, null=True)  # Upload screenshots/logs
    is_anonymous = models.BooleanField(default=False)  # Allow anonymous queries
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    responded_at = models.DateTimeField(blank=True, null=True)  # Track response time
    resolved_at = models.DateTimeField(blank=True, null=True)  # Track resolution time
   
    class Meta:
        ordering = ["-created_at"]  # Show latest queries first

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"

    def mark_as_responded(self):
        """Mark the query as responded and set response time."""
        self.status = "IN_PROGRESS"
        self.responded_at = now()
        self.save()

    def mark_as_resolved(self):
        """Mark the query as resolved and set resolution time."""
        self.status = "RESOLVED"
        self.resolved_at = now()
        self.save()


# Encrypt The Workspace

# Generate a unique key for encryption (Store this securely)
SECRET_KEY = base64.urlsafe_b64encode(os.urandom(32))
cipher = Fernet(SECRET_KEY)

class OrganizationProtection(models.Model):
    organization = models.OneToOneField('your_app.Organization', on_delete=models.CASCADE)
    encrypted_password = models.TextField()  # AES encrypted password
    protection_status = models.BooleanField(default=False)  # Default is False
    failed_attempts = models.IntegerField(default=0)  # Track failed login attempts
    unlock_time = models.DateTimeField(null=True, blank=True)  # Auto-unlock after timeout
    reset_token = models.CharField(max_length=50, null=True, blank=True)  # Reset token for admin
    created_at = models.DateTimeField(auto_now_add=True)

    def set_password(self, raw_password):
        """Encrypt and store password"""
        encrypted = cipher.encrypt(raw_password.encode())
        self.encrypted_password = encrypted.decode()

    def check_password(self, raw_password):
        """Verify encrypted password"""
        try:
            decrypted = cipher.decrypt(self.encrypted_password.encode()).decode()
            return decrypted == raw_password
        except:
            return False  # If decryption fails, password is incorrect

    def generate_reset_token(self):
        """Generate a secure reset token"""
        self.reset_token = get_random_string(50)
        return self.reset_token

    def reset_password(self, new_password):
        """Reset password using a new one"""
        self.set_password(new_password)
        self.reset_token = None  # Remove reset token after reset

    def __str__(self):
        return f"Protection for {self.organization.name}"



