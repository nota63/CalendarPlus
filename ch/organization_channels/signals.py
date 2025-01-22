
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.contrib.auth.models import User
from .models import Channel, Ban



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



# Signal to send email to banned user 

@receiver(post_save, sender=Ban)
def send_ban_notification(sender, instance, created, **kwargs):
    if created:  
        user = instance.user
        channel = instance.channel
        organization = instance.organization
        banned_by = instance.banned_by
        reason = instance.reason
        duration = "Permanent" if not instance.end_time else f"until {instance.end_time.strftime('%Y-%m-%d %H:%M:%S')}"

        # Email subject and body
        subject = f"You have been banned from the channel: {channel.name}"
        message = (
            f"Hello {user.username},\n\n"
            f"You have been banned from the channel '{channel.name}' in the organization '{organization.name}'.\n"
            f"Details:\n"
            f"- Banned by: {banned_by.username}\n"
            f"- Reason: {reason or 'No specific reason provided'}\n"
            f"- Ban Duration: {duration}\n\n"
            f"If you think this is a mistake, please contact the organization admin.\n\n"
            f"Best regards,\n"
            f"The {organization.name} Team"
        )

        # Send the email
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],  
            fail_silently=False,
        )

