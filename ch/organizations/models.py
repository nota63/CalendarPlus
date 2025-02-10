from django.db import models
from accounts.models import Organization, MeetingOrganization
from django.contrib.auth.models import User
from django.utils import timezone

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

     
