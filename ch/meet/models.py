from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from pytz import timezone as pytz_timezone
# Create your models here.
# create meeting model

class Meeting(models.Model):
    title = models.CharField(max_length=100, null=True)
    date = models.DateField(null=True)
    time = models.TimeField(null=True)
    meeting_link=models.TextField(null=True)
    meeting_type=models.CharField(max_length=100, choices=(('Task','Task'),('Standup','Standup'),('Personal','Personal'),('Team','Team')), null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    admin = models.ForeignKey(User, related_name='admin_user', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.title} - {self.user.username} on {self.date}"

# create model for custom meeting reminders

# class Reminder(models.Model):
#     meeting=models.ForeignKey(Meeting, on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     reminder_datetime=models.DateTimeField()

#     def __str__(self):
#         return f"Reminder for {self.user.username} - {self.meeting.title}"




# attach docs 
class Docs(models.Model):
    meeting=models.ForeignKey(Meeting, null=True,on_delete=models.SET_NULL,related_name='docs')
    user=models.ForeignKey(User, null=True,on_delete=models.SET_NULL)
    notes=models.TextField(blank=True)
    documents=models.FileField(upload_to='mmeting_docs', blank=True)
    task=models.CharField(max_length=1000,null=True, blank=True)
    task_title=models.CharField(max_length=100, null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)  


# model for automate birthday wishes

class Birthday(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)  # Added phone number field
    birthdate = models.DateField()
    message = models.TextField()
    scheduled_time = models.DateTimeField()

    def __str__(self):
        return f"Birthday Wish for {self.name} on {self.birthdate}"
    


# New models 


# model for meeting
class Meets(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE,related_name="created_meetings",blank=True, null=True)  # The person scheduling the meeting (you)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="meetings")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    day_of_week = models.CharField(max_length=10)
    start_time = models.TimeField()
    end_time = models.TimeField()
    participants = models.ManyToManyField(User, related_name='meetings_participants',null=True, blank=True)
    
    def __str__(self):
        return f"{self.title} with {self.user.username} (Created by {self.creator}) on {self.day_of_week}"
    

    
# model for custom reminders

class Reminder(models.Model):
    meeting = models.ForeignKey('Meets', on_delete=models.CASCADE, related_name='reminders', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reminders', null=True, blank=True)
    reminder_time = models.DateTimeField(null=True, blank=True)
    created_at= models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f'Reminder for {self.meeting.title}'
    

    class Meta:
        ordering = ['reminder_time']
        

# model for send meeting invitations
class MeetInvitation(models.Model):
    meeting = models.ForeignKey('Meets', on_delete=models.CASCADE, related_name='invitations')
    invited_users = models.ManyToManyField(User, related_name='meeting_invitations')  # Allows inviting multiple users
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_meeting_invitations')
    status = models.CharField(
        max_length=10,
        choices=[
            ('Pending', 'Pending'),
            ('Accepted', 'Accepted'),
            ('Declined', 'Declined'),
        ],
        default='Pending'
    )
    sent_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Invitation for {self.meeting.title} by {self.invited_by.username} (Status: {self.status})"

    def accept_invitation(self, user):
        """Accept the invitation for a specific user."""
        if user not in self.invited_users.all():
            raise ValueError(f"{user.username} was not invited to this meeting.")

        if self.status == 'Pending':
            self.status = 'Accepted'
            self.responded_at = timezone.now()
            self.meeting.participants.add(user) 
            self.save()
            return True
        return False

    def reject_invitation(self, user):
        """Reject the invitation for a specific user."""
        if user not in self.invited_users.all():
            raise ValueError(f"{user.username} was not invited to this meeting.")

        if self.status == 'Pending':
            self.status = 'Declined'
            self.responded_at = timezone.now()
            self.save()
            return True
        return False

# contact list
class Contacts(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contacts')
    contact_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='added_by')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} added {self.contact_user.username} to contacts"
    
# add to favourite     

class FavoriteContact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_contacts')
    contact = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'contact')

    def __str__(self):
        return f'{self.contact.username} is a favorite of {self.user.username}'



