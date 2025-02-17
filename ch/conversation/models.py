from django.db import models
from django.contrib.auth import get_user_model
from accounts.models import Organization
from django.utils.timezone import now
from datetime import timedelta, datetime

User = get_user_model()

class Conversation(models.Model):
    """Tracks conversations between two users."""
    organization=models.ForeignKey(Organization,on_delete=models.CASCADE,null=True, blank=True)
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="conversations_initiated")
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="conversations_received")
    created_at = models.DateTimeField(auto_now_add=True)
   

    class Meta:
        unique_together = ("user1", "user2","organization",) 

    def __str__(self):
        return f"Conversation between {self.user1} and {self.user2}"


class Message(models.Model):
    """Stores individual messages within a conversation."""
    organization = models.ForeignKey(Organization,on_delete=models.CASCADE, null=True, blank=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    text = models.TextField(blank=True, null=True) 
    file = models.FileField(upload_to="chat_files/", blank=True, null=True)
    code_snippet = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    REPEAT_CHOICES = [
        ('daily', 'Daily'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('none', 'None'),
        ('custom', 'Custom')  
    ]

    repeat = models.CharField(max_length=55, choices=REPEAT_CHOICES, default='none', null=True, blank=True)
    custom_repeat_datetime = models.DateTimeField(null=True, blank=True) 


    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        preview = self.text[:20] + "..." if self.text else "File Attached"
        return f"Message from {self.sender} - {preview}"


# SCHEDULE A MESSAGE 
class ScheduledMessage(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="scheduled_messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to="scheduled_chat_files/", blank=True, null=True)
    code_snippet = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_sent = models.BooleanField(default=False)
    
    SCHEDULE_CHOICES = [
        ("specific_time", "Specific Time"),
        ("daily", "Daily"),
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
        ("yearly", "Yearly"),
        ("custom", "Custom Interval"),
    ]

    schedule_type = models.CharField(max_length=20, choices=SCHEDULE_CHOICES, default="specific_time")
    scheduled_time = models.DateTimeField(null=True, blank=True)
    custom_interval = models.DurationField(null=True, blank=True, help_text="Applicable for custom intervals")

    class Meta:
        ordering = ["scheduled_time"]

    def send_message(self):
        if not self.is_sent and self.scheduled_time and self.scheduled_time <= now():
            Message.objects.create(
                organization=self.organization,
                conversation=self.conversation,
                sender=self.sender,
                text=self.text,
                file=self.file,
                code_snippet=self.code_snippet,
                timestamp=now(),
            )
            self.is_sent = True
            self.save()

    def __str__(self):
        return f"Scheduled Message by {self.sender} for {self.scheduled_time}"
