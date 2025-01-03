from django.db import models
from accounts.models import Organization
from django.contrib.auth.models import User
from django.utils import timezone
# Create your models here.


class ContactsOrganization(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="contacts")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_contacts")  # User who is storing contacts
    contact = models.ForeignKey(User, on_delete=models.CASCADE, related_name="contacts_of_user")  # Contacted user
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('organization', 'user', 'contact')  

    def __str__(self):
        return f"{self.user.username} - {self.contact.username} ({self.organization.name})"
    

# Emails 

class EmailOrganization(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_emails")
    participant = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_emails")
    message = models.TextField()
    sent_at = models.DateTimeField(default=timezone.now)
    
    
    attachment_1 = models.FileField(upload_to='email_attachments/', null=True, blank=True)
    attachment_2 = models.FileField(upload_to='email_attachments/', null=True, blank=True)
    attachment_3 = models.FileField(upload_to='email_attachments/', null=True, blank=True)
    status = models.CharField(
    max_length=50, 
    choices=[
        ('Delivered', 'Delivered'),
        ('Pending', 'Pending'),
        ('Shipped', 'Shipped'),
        ('Canceled', 'Canceled'),
        # Add other statuses as needed
    ], 
    default='Delivered', null=True, blank=True
)
    def __str__(self):
        return f"Email from {self.sender.username} to {self.participant.username} on {self.sent_at}"
    

# Schedule Email 
class ScheduledEmail(models.Model):
    TEMPLATE_STYLE_CHOICES = [
        ('Professional', 'Professional'),
        ('Modern', 'Modern'),
        ('Attractive', 'Attractive'),
        ('Playful', 'Playful'),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="scheduled_emails")
    participant = models.ForeignKey(User, on_delete=models.CASCADE, related_name="scheduled_to_receive")
    message = models.TextField()
    schedule_time = models.DateTimeField()  
    template_style = models.CharField(max_length=20, choices=TEMPLATE_STYLE_CHOICES, default='Professional')
    is_sent = models.BooleanField(default=False)  
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True)  

    def __str__(self):
        return f"Scheduled email from {self.sender.username} to {self.participant.username} at {self.schedule_time} (Style: {self.template_style})"

    class Meta:
        ordering = ['schedule_time']  