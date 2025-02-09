from django.db import models
from django.contrib.auth.models import User

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messagess")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messagess")
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]
    
    def __str__(self):
        return f"{self.sender} -> {self.receiver}: {self.message}"
