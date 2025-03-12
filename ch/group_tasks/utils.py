from accounts.models import Organization,Profile
from group_tasks.models import Task , MeetingTaskQuery
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail


# send the reply
def send_reply(org_id,task_id,meeting_id,reply_text):
    organization=get_object_or_404(Organization,id=org_id)
    task=get_object_or_404(Task, id=task_id)
    meeting=get_object_or_404(MeetingTaskQuery,id=meeting_id)

    # prepare the reply
    subject=f'Reply from {task.created_by}, to Meeting {meeting.reason}'
    message=f'Hello {task.assigned_to.username},\n {task.created_by.username} Replied to you about your meeting - {meeting.reason}\n Reply:{reply_text}\n Workspace and Task details: Workspace:{organization.name}\n Task:{task.title}\n Thank you, Team CalendarPlus'
    from_email=settings.DEFAULT_FROM_EMAIL
    recipient_list=[task.assigned_to.email]

    send_mail(subject,message,from_email,recipient_list)










