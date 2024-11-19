from django.db import models
from django.contrib.auth. models import User


# Create your models here.
class Room(models.Model):
    room_name = models.CharField(max_length=250)
    users=models.ManyToManyField(User, related_name='rooms', blank=True)
    created_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.room_name
    
    def get_users(self):
        return self.users.all()
    

class Invitation(models.Model):
    room=models.ForeignKey(Room, related_name='invitations', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='invitations', on_delete=models.CASCADE)
    invited_at=models.DateTimeField(auto_now=True)
    accepted=models.BooleanField(default=False)

    def __str__(self):
        return f"Invitation to {self.user.username} for room {self.room.room_name}"
    
    def accept_invitation(self):
        self.accepted= True
        self.room.users.add(self.user)
        self.save()

    def reject_invitation(self):
        self.delete()
        
            
    