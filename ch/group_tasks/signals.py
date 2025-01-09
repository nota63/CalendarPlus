
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail, EmailMessage
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


# Signal to send email about problem is resolved

@receiver(post_save, sender=Problem)
def send_resolution_email(sender, instance, created, **kwargs):
    if instance.is_resolved:
        task_creator = instance.task.created_by
        if task_creator.email:
            organization_name = instance.organization.name
            group_name = instance.group.name
            task_title = instance.task.title
            problem_description = instance.description
            resolved_at = instance.updated_at.strftime('%B %d, %Y, %I:%M %p')  

            html_message = render_to_string('task/email/problem_resolved.html', {
                'task_creator_name': task_creator.username,
                'resolved_by_name': instance.reported_by.username,
                'organization_name': organization_name,
                'group_name': group_name,
                'task_title': task_title,
                'problem_description': problem_description,
                'resolved_at': resolved_at,
                'organization_website': 'http://127.0.0.1:8000/',  
            })

        
            email = EmailMessage(
                subject=f"Problem Resolved in Task: {task_title}",
                body=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,  
                to=[task_creator.email], 
            )
            email.content_subtype = "html" 

       
            email.send(fail_silently=False)