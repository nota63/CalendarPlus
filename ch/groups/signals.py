
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Group, GroupMember

@receiver(post_delete, sender=Group)
def notify_group_deletion(sender, instance, **kwargs):
    group = instance
    org = group.organization
    group_leader = group.team_leader
    

    group_members = GroupMember.objects.filter(group=group).exclude(user=group_leader)
    

    subject = f"Group '{group.name}' Deleted"
    message = f"The group '{group.name}' has been deleted by {group.created_by.username}. Here are the details:\n\n"
    message += f"Organization: {org.name}\n"
    message += f"Group: {group.name}\n"
    message += f"Created by: {group.created_by.username}\n"
    message += f"Team Leader: {group_leader.username}\n\n"
    message += "This action cannot be undone. If you have any questions, please contact the admin."

    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [group_leader.email]
    )


    for member in group_members:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [member.user.email]
        )
