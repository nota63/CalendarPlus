from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from accounts.models import Profile,Organization
from django.db.models.signals import post_delete


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

        The previous admin, {old_admin.user.first_name} {old_admin.user.last_name}, has successfully transferred the ownership to you.

        If you have any questions, feel free to reach out to us.

        Best Regards,
        The CalendarPlus Team
        """
        from_email = settings.DEFAULT_FROM_EMAIL

      
        send_mail(subject, message, from_email, [new_admin.email])

       
        members_subject = f"New Admin in {organization.name}"
        members_message = f"""
        Hello,

        This is to inform you that {new_admin.first_name} {new_admin.last_name} is the new Admin of the organization "{organization.name}".
        
        If you have any questions, feel free to reach out to the new admin.

        Best Regards,
        The CalendarPlus Team
        """

        member_emails = Profile.objects.filter(organization=organization).exclude(user=new_admin).values_list('user__email', flat=True)

       
        send_mail(members_subject, members_message, from_email, member_emails)



# NOTIFY ALL WORKSPACE MEMBERS ABOUT WORKSPACE DELETION

@receiver(post_delete, sender=Organization)
def send_workspace_deletion_email(sender, instance, **kwargs):
    organization = instance 
    members = Profile.objects.filter(organization=organization)

   
    subject = f"Important: Workspace {organization.name} Deleted"
    message = f"""
    Hello,

    We regret to inform you that the workspace "{organization.name}" has been deleted. 
    Please note that this action cannot be undone.

    If you have any questions, feel free to reach out to the support team.

    Best Regards,
    The CalendarPlus Team
    """
    from_email = settings.DEFAULT_FROM_EMAIL

    for member in members:
        send_mail(subject, message, from_email, [member.user.email])
