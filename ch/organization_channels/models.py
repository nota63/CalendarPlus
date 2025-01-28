from django.db import models
from django.contrib.auth.models import User
from accounts.models import Organization , Profile
from django.utils import timezone
from datetime import timedelta
from better_profanity import profanity
from django.core.mail import send_mail
from .utils import send_abusive_message_notification 

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
    is_pinned=models.BooleanField(default=False, null=True, blank=True)
    is_starred=models.BooleanField(default=False,null=True,blank=True)
    # New parent field for threading
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        related_name='replies', 
        blank=True, 
        null=True
    )


    def __str__(self):
        return f"Message by {self.user.username} in {self.channel.name}"
    

    def save(self, *args, **kwargs):
        # Check if the message contains profanity
        if profanity.contains_profanity(self.content):
            self.content = profanity.censor(self.content)

         
            abused_message=AbusedMessage.objects.create(
                message_content=self.content,
                flagged_by=self.user,
                organization=self.organization,
                channel=self.channel,
            )

            activity = ActivityChannel.objects.create(
                user=self.user,
                channel=self.channel,
                organization=self.organization,
                action_type="WARN",
                content=f' Profinity System Detected an Abused message from {abused_message.flagged_by} & Reported to Workspace admin {Channel.created_by} | Warned {abused_message.flagged_by}!'

           )

         
            send_abusive_message_notification(self.user, self.content, self.channel.name, abused_message.message_content,self.organization)

        super().save(*args, **kwargs)
    
 

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
        ("PINNED_MESSAGE",'Pinned message'),
        ('STARRED_MESSAGE','Starred message'),
        ('MESSAGE_REPLY','Message reply'),
        ("SET_RECURRING_MESSAGE",'Set recurring message'),
        ("PREVENT_RECURRING_MESSAGE",'Prevent recurring message'),
        ("WARN",'Warn'),
    ]

    user = models.ForeignKey(User, related_name='activities', on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel, related_name='activities', on_delete=models.CASCADE, null=True, blank=True)
    organization = models.ForeignKey(Organization, related_name='activities', on_delete=models.CASCADE,null=True, blank=True)
    action_type = models.CharField(max_length=50, choices=ACTION_CHOICES)
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
    
    def unban(self):
        """
        Permanently unban the user by deleting the ban record.
        """
        self.delete()

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
    

     # Method to remove access
    def remove_access(self):
        try:
            
            self.delete()
            return True 
        except Exception as e:
       
            print(f"Error removing access: {str(e)}")
            return False


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


# Set recurring Message 


class RecurringMessage(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    recurrence_type = models.CharField(
        max_length=50,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('yearly', 'Yearly'),
            ('custom', 'Custom')
        ]
    )
    recurrence_days = models.JSONField(null=True, blank=True)  
    start_date = models.DateField(auto_now_add=True)  
    end_date = models.DateField(null=True, blank=True)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.text} ({self.recurrence_type})"
    

# RECURRENCE MESSAGE HISTORY 

class RecurrenceHistory(models.Model):
    recurring_message = models.ForeignKey(RecurringMessage, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    sent_at = models.DateTimeField(auto_now_add=True)
    recurrence_type = models.CharField(
        max_length=50,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('yearly', 'Yearly'),
            ('custom', 'Custom')
        ]
    )

    def __str__(self):
        return f"Message '{self.recurring_message.text}' sent on {self.sent_at}"

    class Meta:
        ordering = ['-sent_at']


# COMPANY HANDBOOK

class ChannelEvents(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    event_name = models.CharField(max_length=255)
    event_date = models.DateTimeField()
    event_details = models.TextField()
    event_attachment = models.FileField(upload_to='event_attachments/', null=True, blank=True)
    event_link = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.event_name





# CHANNEL SETTINGS

class ChannelSettingsOrganization(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE,related_name='channel_settings')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='settings')
    channel=models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='settings')

    allow_media_uploads=models.BooleanField(default=True, null=True, blank=True)
    allow_codes=models.BooleanField(default=False,null=True,blank=True)
    secure_from_unwanted_requests=models.BooleanField(default=False, null=True, blank=True)
    allow_polls=models.BooleanField(default=False, null=True, blank=True)
    allow_sharing_access_to_another_workspace=models.BooleanField(default=True, null=True, blank=True)
    track_abusive_messages=models.BooleanField(default=True, null=True, blank=True)
    allow_integrations=models.BooleanField(default=False, null=True, blank=True)
    integration_choices=models.CharField(max_length=100, choices=(('Slack','slack'),('Trello','trello'),('Calendly','calendly')))

    def __str__(self):
        return f'{self.channel.name} settings'
    


# TRACK PERMISSIONS WITHIN THE CHANNEL

class Permission(models.Model):
    CAN_SEND_MESSAGES = 'can_send_messages'
    CAN_EDIT_MESSAGES = 'can_edit_messages'
    CAN_SEND_FILES = 'can_send_files'
    
    PERMISSION_CHOICES = [
        (CAN_SEND_MESSAGES, 'Can Send Messages'),
        (CAN_EDIT_MESSAGES, 'Can Edit Messages'),
        (CAN_SEND_FILES, 'Can Send Files'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='permissions')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='permissions')
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='permissions')
    granted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='permissions_granted')
    granted_at = models.DateTimeField(auto_now_add=True)

  
    permissions = models.JSONField(default=list, blank=True,null=True)

   
    def __str__(self):
        return f"{self.user.username} permissions in {self.channel.name} (Granted by {self.granted_by.username})"

    def grant_default_permissions(self):
        """Grant default permissions to a user by default."""
        default_permissions = [
            self.CAN_SEND_MESSAGES,
            self.CAN_EDIT_MESSAGES,
            self.CAN_SEND_FILES
        ]
        self.permissions = default_permissions
        self.save()

    def add_permission(self, permission):
        """Add a permission to the user."""
        if permission not in self.permissions:
            self.permissions.append(permission)
            self.save()

    def remove_permission(self, permission):
        """Remove a permission from the user."""
        if permission in self.permissions:
            self.permissions.remove(permission)
            self.save()