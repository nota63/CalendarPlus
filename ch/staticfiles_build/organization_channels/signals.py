
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.contrib.auth.models import User
from .models import Channel

@receiver(post_save, sender=Channel)
def send_channel_email(sender, instance, created, **kwargs):
    """
    Send email to users when a new channel is created with specific visibility.
    """
    if created and instance.visibility == 'PRIVATE':
        
        users_to_notify = instance.allowed_members.all()

        for user in users_to_notify:
            send_channel_notification_email(user, instance)

def send_channel_notification_email(user, channel):
    """
    Send a notification email to the user about the new channel.
    """
    subject = f"New Channel Invitation: {channel.name}"
    message = f"You have been invited to join the channel '{channel.name}' in the organization '{channel.organization.name}'."
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list)
