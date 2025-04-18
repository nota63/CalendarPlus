from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings


# send task assignment email
def send_task_assignment_email(user, task, group, organization):
    try:
        subject = f"New Task Assigned: {task.title}"
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = user.email

        context = {
            'user': user,
            'task': task,
            'group': group,
            'organization': organization,
        }

        html_content = render_to_string('task/email/task_assignment_widget_email.html', context)
        text_content = f"You have been assigned a task: {task.title}. Please check your task board."

        email = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        email.attach_alternative(html_content, "text/html")
        email.send()
    except Exception as e:
        print(f"Failed to send task assignment email: {str(e)}")
