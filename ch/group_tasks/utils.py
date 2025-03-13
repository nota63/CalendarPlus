from accounts.models import Organization,Profile
from group_tasks.models import Task , MeetingTaskQuery
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from groups.models import Group

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



# SEND EMAIL AFTER TASK DELETION

def after_task_deletion(org_id, group_id,task_id):
    organization=get_object_or_404(Organization,id=org_id)
    task=get_object_or_404(Task, id=task_id)
    group=get_object_or_404(Group, id=group_id)


    subject=f'Task {task.title} Deletion,'
    message =f'Task deleted by {task.created_by.username},\n Hello {task.assigned_to.username},\n The task from the group:{group.name} Has been deleted!\n please review the following info\n Task:{task.title}-{task.deadline}-{task.priority}\n Workspace:{organization.name}\n Group:{group.name}\n Thank you,\n Team CalendarPlus'
    from_email=settings.DEFAULT_FROM_EMAIL
    recipient_list=[task.assigned_to.email]

    send_mail(subject,message,from_email,recipient_list)








