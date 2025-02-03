from django.db import models
from accounts.models import Organization
from django.contrib.auth.models import User


# Create your models here.
# models.py
class Conversation(models.Model):
    user_1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations_as_user_1')
    user_2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations_as_user_2')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='conversations')

    def __str__(self):
        return f"Conversation between {self.user_1.username} and {self.user_2.username}"
    
    def get_other_user(self, user):
        # Method to return the other user in the conversation
        return self.user_2 if user == self.user_1 else self.user_1


# models.py
class Message(models.Model):
    organization=models.ForeignKey(Organization, on_delete=models.CASCADE,related_name='dm_organizations',null=True,blank=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages',null=True,blank=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username} at {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']  
