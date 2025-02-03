from django.db import models
from django.contrib.auth.models import User
from accounts.models import Organization, Profile
from django.db.models import Q

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
    

# UNIQUE ROOM FOR DIRECT MESSAGES 

class DMRoom(models.Model):
    organization = models.ForeignKey("Organization", on_delete=models.CASCADE, related_name="dm_rooms")
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="dm_rooms_as_user1")
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="dm_rooms_as_user2")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "user1", "user2"],
                name="unique_dm_room"
            )
        ]

    def __str__(self):
        return f"DM Room: {self.user1.username} & {self.user2.username} in {self.organization.name}"

    @classmethod
    def get_or_create_dm_room(cls, organization, user_a, user_b):
        """Fetches or creates a unique DM room between two users within an organization."""
        room, created = cls.objects.get_or_create(
            organization=organization,
            user1=min(user_a, user_b, key=lambda u: u.id),
            user2=max(user_a, user_b, key=lambda u: u.id)
        )
        return room