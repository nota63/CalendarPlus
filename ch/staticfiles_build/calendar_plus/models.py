from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
import secrets
from datetime import datetime, timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
import uuid
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError




# Holidays
class Holiday(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="holidays")
    start_date = models.DateField()  
    end_date = models.DateField(null=True, blank=True)  
    description = models.CharField(max_length=255, blank=True)  
    is_recurring = models.BooleanField(default=False)  

    class Meta:
        unique_together = ('user', 'start_date', 'end_date') 

    def clean(self):
        if self.end_date and self.end_date < self.start_date:
            raise ValidationError("End date must be greater than or equal to start date.")
        
        
        if self.is_recurring and self.end_date:
            raise ValidationError("Recurring holidays cannot span multiple days.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        if self.end_date:
            return f"{self.user.username} - {self.start_date} to {self.end_date} ({'Recurring' if self.is_recurring else 'One-time'})"
        return f"{self.user.username} - {self.start_date} ({'Recurring' if self.is_recurring else 'One-time'})"

# Event Section 

class Event(models.Model):
    EVENT_TYPES = [
        ('one_on_one', 'One-on-One'),
        ('group', 'Group Meeting'),
    ]
    
    LOCATION_CHOICES = [
        ('Google Meet', 'Google Meet'),
        ('Zoom', 'Zoom'),
        ('Phone Call', 'Phone Call'),
        ('In Person Meeting', 'In Person Meeting'),
    ]
    
    LOCATION_ICONS = {
        'Google Meet': 'fab fa-google',
        'Zoom': 'fab fa-zoom',
        'Phone Call': 'fas fa-phone',
        'In Person Meeting': 'fas fa-users',
    }

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="events", null=True, blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, default='one_on_one', null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    duration = models.PositiveIntegerField(null=True, blank=True)
    buffer_time = models.PositiveIntegerField(default=0, null=True, blank=True)
    is_recurring = models.BooleanField(default=False, null=True, blank=True)
    location = models.CharField(
        max_length=100, choices=LOCATION_CHOICES, default='Google Meet', null=True, blank=True
    )
    slug = models.SlugField(unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.title}-{uuid.uuid4().hex[:8]}")
        super().save(*args, **kwargs)

    def get_location_icon(self):
        return self.LOCATION_ICONS.get(self.location, 'fas fa-map-marker-alt')

    def __str__(self):
        return f"{self.title} ({self.user.username})"


# Booking Model

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    event = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='bookings')
    invitee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    event_host=models.ForeignKey(User,on_delete=models.CASCADE, related_name='event_host', blank=True,null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Booking for {self.event.title} by {self.invitee.username} at {self.start_time}"

    def is_accepted(self):
        return self.status == 'confirmed'

    def cancel(self):
        self.status = 'cancelled'
        self.save()

    def confirm(self):
        self.status = 'confirmed'
        self.save()


    