from django.db import models
from django.contrib.auth.models import User

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
    

