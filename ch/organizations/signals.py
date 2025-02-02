from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from accounts.models import Profile
@receiver(post_save, sender=Profile)


def send_ownership_transfer_email(sender, instance, created, **kwargs):
    if not created and instance.is_admin:  
        organization = instance.organization
        new_admin = instance.user
        old_admin = Profile.objects.get(organization=organization, is_admin=True, user__is_active=True)

    
        subject = f"Ownership Transfer in {organization.name}"
        message = f"""
        Hello {new_admin.first_name},  # Using first_name for a personalized greeting

        You have been promoted to the position of Admin in the organization "{organization.name}".
        
        Organization Details:
        - Name: {organization.name}
        - Total Channels: {organization.channels.count()}
        - Total Users: {organization.profiles.count()}

        The previous admin, {old_admin.user.username} {old_admin.user.last_name}, has successfully transferred the ownership to you.

        If you have any questions, feel free to reach out to us.

        Best Regards,
        The CalendarPlus Team
        """
        from_email = settings.DEFAULT_FROM_EMAIL

        
        send_mail(subject, message, from_email, [new_admin.email])  