from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


def send_task_assigned_email(user, task, organization, group):
    """
    Send an email to the assigned user when a task is assigned to them.
    """
    subject = f"Task Assigned: {task.title}"
    
    # Prepare the email content
    html_message = render_to_string('task/email/task_assigned.html', {
        'task': task,
        'organization': organization,
        'group': group,
    })
    
    # Strip the HTML tags for the plain text version
    plain_message = strip_tags(html_message)
    
    # Create email message
    email = EmailMessage(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,  # Sender email address
        [user.email],  # Recipient email address
    )
    
    # Attach the HTML content as an alternative
    email.content_subtype = "html"  # This makes sure the email is sent as HTML
    email.body = html_message  # Set the body to HTML content

    # Send the email
    email.send()
