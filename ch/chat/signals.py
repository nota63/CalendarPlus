from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Room
from django.template.loader import render_to_string

@receiver(m2m_changed, sender=Room.users.through)
def send_invite_emails(sender, instance, action, **kwargs):
    if action == 'post_add':
        # get all users who were added
        user_ids= kwargs.get('pk_set', [])
        if user_ids:
            users= instance.users.filter(id__in=user_ids)
            usernames = [user.username for user in users]
            # get email addresses of all users
            email_list= [user.email for user in users if user.email]
            html_message=render_to_string('chat/chat_backends.html', {'username':usernames})

            send_mail(
                subject='you are invited to a room',
                message=f'You have been invited to join the room: {instance.room_name}.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=email_list,
                html_message=html_message,
                fail_silently=False,
            )