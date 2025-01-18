from django.db import models
from django.contrib.auth.models import User
from accounts.models import Organization , Profile

# Create your models here.


# Model for channels 

class Channel(models.Model):
    CHANNEL_TYPES = [
        ('BLANK', 'Blank Channel'),
        ('PROJECT_STARTER', 'Project Starter Kit'),
        ('HELP_REQUESTS', 'Help Requests Process'),
        ('TEAM_SUPPORT', 'Team Support'),
        ('FEEDBACK', 'Feedback Intake and Triage'),
        ('ONBOARDING', 'New Hire Onboarding'),
        ('COACHING', '1:1 Coaching'),
        ('SALES_TRACKING', 'Sales Deal Tracking'),
    ]

    VISIBILITY_CHOICES = [
        ('PUBLIC', 'Public - Anyone in Organization'),
        ('PRIVATE', 'Private - Specific People Only'),
    ]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name='channels'
    )
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='created_channels'
    )
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=CHANNEL_TYPES, default='BLANK')
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='PUBLIC')
    allowed_members = models.ManyToManyField(User, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
    def __str__(self):
        return f"{self.name} ({self.get_type_display()}) - {self.get_visibility_display()}"

    










