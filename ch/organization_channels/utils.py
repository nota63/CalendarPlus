from django.core.mail import send_mail
from django.conf import settings


def send_abusive_message_notification(user, message_content, channel_name, flagged_message_content, organization):
    """
    Sends an email to the user who flagged a message containing abusive content
    and to the organization admin notifying them about the flagged message.
    """
    
    subject_to_user = 'Important: Abusive Message Flagged'
    message_to_user = f"""
    Hello {user.username},

    We noticed that your message in the channel "{channel_name}" has been flagged for containing abusive words.

    The message that was flagged:
    "{message_content}"

    We urge you to follow our community guidelines and avoid using offensive language. 
    Here are some tips to help you:
    - Always communicate respectfully with others.
    - If you feel frustrated or upset, try taking a moment to calm down before posting.
    - Refrain from using words that may hurt or offend others.
    - Please be mindful of the language you use in the community.

    We appreciate your cooperation in maintaining a safe and positive space for everyone.

    Best regards,
    The Admin Team
    """

   
    send_mail(
        subject_to_user,
        message_to_user,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],  
        fail_silently=False,
    )

    
    subject_to_admin = 'Alert: Abusive Message Flagged in Your Organization'
    message_to_admin = f"""
    Hello {organization.created_by.username},

    This is to inform you that a message from {user.username} in the channel "{channel_name}" has been flagged for containing abusive language.

    The flagged message:
    "{message_content}"

    The details of the user who flagged the message:
    - Username: {user.username}
    - Email: {user.email}
    - Organization: {organization.name}
    - Channel: {channel_name}

    Please review the message and take any necessary actions.

    Thank you for your attention in maintaining a positive and respectful environment for your organization.

    Best regards,
    The Admin Team
    """

    
    send_mail(
        subject_to_admin,
        message_to_admin,
        settings.DEFAULT_FROM_EMAIL,
        [organization.created_by.email], 
        fail_silently=False,
    )