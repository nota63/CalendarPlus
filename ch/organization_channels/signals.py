
from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.contrib.auth.models import User
from .models import Channel, Ban
from accounts.models import Organization, Profile


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



# SEND CHANNEL DELETION MAIL!

@receiver(post_delete, sender=Channel)
def send_channel_deletion_email(sender, instance, **kwargs):

    organization = instance.organization
    user = instance.created_by


    profiles = Profile.objects.filter(organization=organization)
    
 
    recipient_emails = [profile.user.email for profile in profiles if profile.user.email]

   
    subject = f"Channel Deleted: {instance.name}"
    message = f"Dear Members,\n\nWe wanted to inform you that {user.username} has deleted the channel '{instance.name}' from the organization '{organization.name}'.\n\nBest regards,\nYour Team"


    if recipient_emails:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipient_emails,
            fail_silently=False,
        )



# NOTIFY THE USER ABOUT UNBANNED

@receiver(post_save, sender=Ban)
def send_unban_email(sender, instance, created, **kwargs):
   
    if not instance.is_active() and created:  
        try:
            subject = f'You have been unbanned from {instance.channel.name}'
            message = (
                f"Hello {instance.user.username},\n\n"
                f"We wanted to inform you that you have been unbanned from the channel '{instance.channel.name}' "
                f"in the organization '{instance.organization.name}'.\n\n"
                f"The unban was initiated by {instance.banned_by.username}.\n\n"
                f"Reason: {instance.reason or 'No specific reason provided'}\n"
                f"Your ban started on: {instance.start_time}\n"
                f"Your ban ended on: {instance.end_time}\n\n"
                "Feel free to rejoin the discussions!\n\n"
                "Best regards,\n"
                f"The {instance.organization.name} Team"
            )
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [instance.user.email])
        except Exception as e:
            print(f"Error sending unban email: {e}")


        