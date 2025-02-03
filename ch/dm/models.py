from django.db import models
from django.contrib.auth.models import User
from accounts.models import Organization, Profile


# Create your models here.


class DirectMessage(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)  
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]  

    def __str__(self):
        return f"DM from {self.sender} to {self.receiver} in {self.organization}"