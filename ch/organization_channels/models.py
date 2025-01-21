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

    

# Save messages into database

class Message(models.Model):
    channel = models.ForeignKey(Channel, related_name='messages', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    audio = models.FileField(upload_to='uploads/audio/', null=True, blank=True)  
    video = models.FileField(upload_to='uploads/video/', null=True, blank=True)  
    timestamp = models.DateTimeField(auto_now_add=True)
    organization = models.ForeignKey(Organization, related_name='messages', on_delete=models.CASCADE)

    def __str__(self):
        return f"Message by {self.user.username} in {self.channel.name}"
    
 

# Link

class Link(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    channel = models.ForeignKey(Channel, related_name='links', on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, related_name='links', on_delete=models.CASCADE)  # Assuming Organization model exists
    text = models.CharField(max_length=255)
    link = models.URLField()
    timestamp=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text


# Mention

class Mention(models.Model):
    channel = models.ForeignKey(Channel, related_name='mentions', on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, related_name='mentions', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='mentions', on_delete=models.CASCADE)
    mentioned_user = models.ForeignKey(User, related_name='mentioned_by', on_delete=models.CASCADE)  # User being mentioned
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} mentioned {self.mentioned_user.username} in {self.channel.name}'


# Track inside channel activity

class ActivityChannel(models.Model):
    ACTION_CHOICES = [
        ('MESSAGE', 'Message'),
        ('MENTION', 'Mention'),
        ('EMOJI', 'Emoji'),
        ('LINK', 'Link'),
        ('FILE_UPLOAD', 'File Upload'),
        ('JOIN', 'Join'),
        ('LEAVE', 'Leave'),
        ("DATA_EXPORT",'Data export'),
        ('EXPLORE_STATISTICS','Explore statistics'),
        ("MESSAGES_DELETE",'Messages delete'),
        ("MESSAGE_DELETE",'Message_delete'),
    ]

    user = models.ForeignKey(User, related_name='activities', on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel, related_name='activities', on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, related_name='activities', on_delete=models.CASCADE)
    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES)
    content = models.TextField(null=True, blank=True) 
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} performed {self.get_action_type_display()} in {self.channel.name}"

    class Meta:
        ordering = ['-timestamp'] 