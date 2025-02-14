from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Conversation(models.Model):
    """Tracks conversations between two users."""
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="conversations_initiated")
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="conversations_received")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user1", "user2") 

    def __str__(self):
        return f"Conversation between {self.user1} and {self.user2}"


class Message(models.Model):
    """Stores individual messages within a conversation."""
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
