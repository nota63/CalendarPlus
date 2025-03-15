from accounts.models import Organization,Profile
from group_tasks.models import Task , MeetingTaskQuery
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from groups.models import Group
from django.template.loader import render_to_string
from django.utils.html import strip_tags


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


# SEND TASK SUBMISSION APPROVAL TO THE MANAGER
def task_submission_approval(org_id, group_id, task_id):
    organization = get_object_or_404(Organization, id=org_id)
    group = get_object_or_404(Group, id=group_id, organization=organization)
    task = get_object_or_404(Task, id=task_id, group=group, organization=organization)

    # ✅ Get manager email (task.created_by)
    manager_email = task.created_by.email

    # ✅ Render email content
    subject = f"Approval Required: Task '{task.title}' Submission"
    html_message = render_to_string("task/email/task_submission_email.html", {
        "task": task,
        "organization": organization,
        "group": group,
    })
    plain_message = strip_tags(html_message)  # Convert HTML to plain text

    # ✅ Send email
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,  
        [manager_email],
        html_message=html_message,
        fail_silently=False,
    )


# Share task details to workspace members
def send_task_details(org_id, group_id, task_id, selected_members):
    organization = get_object_or_404(Organization, id=org_id)
    group = get_object_or_404(Group, id=group_id, organization=organization)
    task = get_object_or_404(Task, id=task_id, group=group, organization=organization)

    # Fetch members' emails
    members = Profile.objects.filter(user_id__in=selected_members, organization=organization)
    recipient_emails = [member.user.email for member in members]

    subject = f"📌 Task Collaboration Request: {task.title} | {organization.name}"

    message = f"""
    Dear Team,  

    I hope you're doing well. I wanted to share an important task with you that was assigned to me in our workspace **{organization.name}**.  
    Your expertise and insights would be greatly appreciated in helping me accomplish it effectively.  

    ### **Task Details**  
    - **Workspace:** {organization.name}  
    - **Group:** {group.name}  
    - **Task Title:** {task.title}  
    - **Description:** {task.description}  
    - **Deadline:** {task.deadline.strftime('%B %d, %Y')}  
    - **Priority:** {task.priority}  

    ### **Why I Need Your Help**  
    I believe your knowledge and experience can provide valuable insights on how to efficiently complete this task. If you have any suggestions, feedback, or guidance, I'd love to hear from you.  

    ### **How to Reach Me?**  
    You can connect with me directly through **Calendar Plus DMs** or drop me an email at **{task.assigned_to.email}**.  

    I truly appreciate your time and support. Looking forward to collaborating with you.  

    Best Regards,  
    **{task.assigned_to.get_full_name()}**  
    *{task.assigned_to.email}*  
    """

    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = recipient_emails

    send_mail(subject, message, from_email, recipient_list)


# Notify the task assignee about task approval or rejection by manager

def send_task_notification_email(org_id, group_id, task_id, action):
    """
    Sends an email notification to task.assigned_to when a task is approved or rejected.
    """
    # ✅ Fetch Task, Organization, and Group
    task = get_object_or_404(Task, id=task_id, group_id=group_id, organization_id=org_id)
    organization = get_object_or_404(Organization, id=org_id)
    group = get_object_or_404(Group, id=group_id)

    # ✅ Get Assignee Details
    assignee = task.assigned_to
    assignee_name = assignee.get_full_name() if assignee.get_full_name() else assignee.username

    # ✅ Set Subject & Message Based on Action
    if action == "approve":
        subject = f"✅ Task Approved: {task.title} - {organization.name}"
        message = (
            f"Dear {assignee_name},\n\n"
            f"Your task **'{task.title}'** has been **approved** ✅ by the manager in the organization **{organization.name}**, under the group **{group.name}**.\n"
            f"The task is now marked as **Completed**.\n\n"
            f"📅 Deadline: {task.deadline.strftime('%Y-%m-%d %H:%M') if task.deadline else 'No deadline'}\n"
            f"📝 Task Description: {task.description}\n\n"
            f"Keep up the great work!\n\n"
            f"Best Regards,\n"
            f"Calendar Plus Team"
        )
    elif action == "reject":
        subject = f"❌ Task Rejected: {task.title} - {organization.name}"
        message = (
            f"Dear {assignee_name},\n\n"
            f"Your task **'{task.title}'** has been **rejected** ❌ in the organization **{organization.name}**, under the group **{group.name}**.\n"
            f"The task progress is now set to **50%** and requires **changes** before approval.\n\n"
            f"📅 Deadline: {task.deadline.strftime('%Y-%m-%d %H:%M') if task.deadline else 'No deadline'}\n"
            f"📝 Task Description: {task.description}\n\n"
            f"Please make the necessary updates and resubmit the task.\n\n"
            f"Best Regards,\n"
            f"Calendar Plus Team"
        )

    # ✅ Send Email
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,  
        [assignee.email],  
        fail_silently=False,
    )


