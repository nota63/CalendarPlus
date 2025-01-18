from django.db import models
from accounts.models import Profile , Organization, EventOrganization, BookingOrganization, MeetingOrganization
from django.contrib.auth.models import User


# Create your models here.

class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('delete_user', 'Deleted User'),
        ('delete_meetings', 'Deleted Meetings'),
        ('delete_events', 'Deleted Events'),
        ('delete_bookings', 'Deleted Bookings'),
    ]
    
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='activity_logs')
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    target_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deleted_by_admin', null=True, blank=True)
    
    actions = models.ManyToManyField(
        'Action', 
        related_name='activity_logs', 
        blank=True
    )
    action_details = models.TextField(null=True, blank=True)  
    timestamp = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        actions = ', '.join([action.name for action in self.actions.all()])  
        return f"Actions: {actions} on {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']  


class Action(models.Model):
    name = models.CharField(max_length=50, choices=ActivityLog.ACTION_CHOICES)

    def __str__(self):
        return self.get_name_display()