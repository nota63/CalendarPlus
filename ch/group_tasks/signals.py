
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Problem

@receiver(post_save, sender=Problem)
def send_problem_report_email(sender, instance, created, **kwargs):
    if created:
        task = instance.task
        organization = instance.organization
        group = instance.group


        subject = f"Problem Reported for Task: {task.title}"
        message = render_to_string('task/email/problem_reported.html', {
            'task_title': task.title,
            'task_description': task.description,
            'task_created_by': task.created_by.username,
            'deadline':task.deadline,
            'organization_name': organization.name,
            'group_name': group.name,
            'problem_description': instance.description,
            'reported_by': instance.reported_by.username,
            'created_at': instance.created_at,
            'problem_id': instance.id,
            'is_resolved': instance.is_resolved,
        })

        send_mail(
            subject,
            '',  
            settings.EMAIL_HOST_USER,
            [task.created_by.email],  
            fail_silently=False,
            html_message=message  
        )