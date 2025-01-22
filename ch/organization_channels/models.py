from django.db import models
from django.contrib.auth.models import User
from accounts.models import Organization , Profile
from django.utils import timezone
from datetime import timedelta

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
        ("LINK_DELETE",'Link delete'),
        ('MESSAGE_EDITED','Message edited'),
        ("LINK_EDITED",'Link edited'),
        ('FILTERED_MESSAGES','Filtered messages'),
        ("BAN_USER",'Ban user'),
        ("CHANNEL_ACCESS",'Channel access'),
        ("SET_RETENTION_POLICY",'Set retention policy'),
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


# BAN USERS FROM CHANNEL


class Ban(models.Model):
    BAN_CHOICES = [
        ('1_day', '1 Day'),
        ('1_week', '1 Week'),
        ('1_month', '1 Month'),
        ('permanent', 'Permanent'),
    ]

    organization = models.ForeignKey(
        Organization, related_name="bans", on_delete=models.CASCADE
    )
    channel = models.ForeignKey(
        Channel, related_name="bans", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User, related_name="banned_entries", on_delete=models.CASCADE
    )
    banned_by = models.ForeignKey(
        User, related_name="issued_bans", on_delete=models.CASCADE
    )
    reason = models.TextField(null=True, blank=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)  
    duration = models.CharField(max_length=10, choices=BAN_CHOICES, default='permanent')

    def set_end_time(self):
        """
        Set the end time based on the ban duration.
        """
        if self.duration == '1_day':
            self.end_time = self.start_time + timedelta(days=1)
        elif self.duration == '1_week':
            self.end_time = self.start_time + timedelta(weeks=1)
        elif self.duration == '1_month':
            self.end_time = self.start_time + timedelta(weeks=4)
        elif self.duration == 'permanent':
            self.end_time = None  
        self.save()

    def is_active(self):
        """
        Checks if the ban is still active.
        """
        return self.end_time is None or timezone.now() < self.end_time

    def __str__(self):
        return f"{self.user.username} banned from {self.channel.name} by {self.banned_by.username}"
    



# Give Channel accesss to other organization

class ChannelAccess(models.Model):
    channel = models.ForeignKey('Channel', on_delete=models.CASCADE, related_name='accesses')
    owning_organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE, 
        related_name='owned_channel_accesses',
        help_text="The organization that owns the channel."
    )
    granted_to_organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE, 
        related_name='granted_channel_accesses',
        help_text="The organization being granted access to the channel."
    )
    granted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='granted_accesses')
    granted_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('channel', 'granted_to_organization')  
        verbose_name = 'Channel Access'
        verbose_name_plural = 'Channel Accesses'

    def __str__(self):
        return (
            f"{self.granted_to_organization.name} has access to {self.channel.name} "
            f"(granted by {self.granted_by.username}, owned by {self.owning_organization.name})"
        )


# RETENTION POLICY

class RetentionPolicy(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='retention_policies'
    )
    channel = models.ForeignKey(
        Channel,
        on_delete=models.CASCADE,
        related_name='retention_policies'
    )
    retention_period = models.IntegerField(
        choices=[
            (30, '30 Days'),
            (45, '45 Days'),
            (90, '3 Months'),
            (180, '6 Months'),
            (365, '1 Year'),
            (0, 'Custom'),  
        ],
        default=30,
        help_text="Retention period for auto-deleting messages"
    )
    custom_days = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Enter custom days if retention period is set to 'Custom'"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_retention_policies'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Retention Policy: {self.get_retention_period_display()} for {self.channel.name}"

    class Meta:
        unique_together = ('organization', 'channel')

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.retention_period == 0 and not self.custom_days:
            raise ValidationError("Custom days must be specified when retention period is set to 'Custom'.")
        if self.retention_period != 0 and self.custom_days:
            raise ValidationError("Custom days should only be specified for 'Custom' retention period.")
        


# Abused Messages 

class AbusedMessage(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="abused_messages")
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name="abused_messages")
    message_content = models.TextField(help_text="Content of the abused message")
    flagged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="flagged_abused_messages")
    flagged_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the message was flagged")

    def __str__(self):
        return f"Abused Message in {self.channel.name} flagged by {self.flagged_by.username if self.flagged_by else 'Unknown'}"

    class Meta:
        verbose_name = "Abused Message"
        verbose_name_plural = "Abused Messages"
        ordering = ['-flagged_at']