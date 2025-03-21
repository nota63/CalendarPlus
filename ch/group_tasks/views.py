from django.shortcuts import render, redirect , get_list_or_404
from .models import (Task, TaskNote, TaskComment , TaskTag, ActivityLog,RecentVisit,MeetingTaskQuery,CommunicateTask,TaskReminder
                     
                     ,PendingRewardNotification,CalPoints,AutomationTask)
from accounts.models import Organization, Profile
from groups.models import Group
from django.views import View
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import Http404
from .models import Group, GroupMember, Task
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.conf import settings
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from .models import TaskTimer
from datetime import timedelta
from django.utils.timezone import now
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from decimal import Decimal
from .models import TaskTimeTracking, Problem,ActivityLog
import io
from django.http import FileResponse, JsonResponse
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.template.loader import render_to_string
from premailer import transform  
import mimetypes
from reportlab.lib.pagesizes import letter
import base64
import json
import os
from django.core.files.base import ContentFile
from django.core.exceptions import ObjectDoesNotExist
from .utils import (send_reply,after_task_deletion,task_submission_approval,send_task_details,send_task_notification_email)
# Create your views here.


# Task creation
@login_required
def create_task(request, org_id, group_id):

    group = get_object_or_404(Group, id=group_id, organization_id=org_id)
    organization = get_object_or_404(Organization, id=org_id)
    

    if request.user != group.team_leader:
        messages.error(request, _("You do not have permission to create tasks for this group."))
        raise Http404
    
    if request.method == 'POST':
 
        email = request.POST.get('email')
        title = request.POST.get('title')
        description = request.POST.get('description')
        priority = request.POST.get('priority')
        deadline = request.POST.get('deadline')
        
        try:
          
            assigned_user = User.objects.filter(email=email).first()
            if not assigned_user:
                raise ValidationError(_('No user found with this email address.'))
            
        
            group_member = GroupMember.objects.filter(group=group, user=assigned_user).first()
            if not group_member:
                raise ValidationError(_('This user is not a member of the group.'))
            
        
            task = Task.objects.create(
                title=title,
                description=description,
                assigned_to=assigned_user,
                created_by=request.user,
                group=group,
                organization=group.organization,
                priority=priority,
                deadline=deadline,
            )

        
            subject = f"New Task Assigned: {task.title}"
            message = f"""
            Hello {assigned_user.first_name},
            
            You have been assigned a new task in the group: {group.name} under the organization: {organization.name}.
            
            Task Title: {task.title}
            Description: {task.description}
            Priority: {task.priority}
            Deadline: {task.deadline}
            
            Group Details:
            Group Name: {group.name}
            Description: {group.description}
            
            Organization Details:
            Organization Name: {organization.name}
            Description: {organization.description}
            
            Please login to your account to view the task and start working on it.
            
            Best regards,
            The {organization.name} Team
            """

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [assigned_user.email],
                fail_silently=False,
            )

            messages.success(request, _('Task created successfully and email sent to the assigned user!'))
            return redirect('create_task', org_id=organization.id, group_id=group.id)  
            
        except ValidationError as e:
            messages.error(request, e.message)
    
    return render(request, 'task/create_task.html', {
        'group': group,
    })



# Display the tasks in calendar
from .models import AddDay,SubTask,AttachmentsTasksApp
from app_marketplace.models import InstalledMiniApp


@login_required
def task_calendar(request, org_id, group_id):
    group = get_object_or_404(Group, id=group_id, organization_id=org_id)
    organization = get_object_or_404(Organization, id=org_id)

    if not GroupMember.objects.filter(group=group, user=request.user).exists():
        raise Http404("You are not a member of this group.")

    
    priority_filter = request.GET.get('priority', None)


    tasks = Task.objects.filter(group=group, assigned_to=request.user)

    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)

    tasks = tasks.order_by('-created_at')


    paginator = Paginator(tasks, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    task_data = []
    for task in page_obj:
        task_in_my_day = AddDay.objects.filter(task=task, user=request.user).exists()
        task_data.append({
            'title': task.title,
            'description': task.description,
            'priority': task.priority,
            'start': task.deadline.strftime('%Y-%m-%d'),
            'progress': task.progress,
            'id': task.id,
            'in_my_day': task_in_my_day  
        })

    
    # Check if "Extend Tasks" app is installed
    extend_tasks = InstalledMiniApp.objects.filter(organization=organization, user=request.user, mini_app__name="Extend Tasks")

    if extend_tasks.exists():
       print("EXTEND TASKS FOUND::")
    else:
       print("NOT FOUND!")

    return render(request, 'task/task_calendar.html', {
        'tasks': task_data,
        'group': group,
        'organization': organization,
        'page_obj': page_obj,
        'extend_tasks':extend_tasks,
    })

# EXTENDED TASKS CONTROLS APP ------------------------------------------------------------------------------------------------------------------
from app_marketplace.check_org_membership import check_org_membership

# Cancel the task

@check_org_membership
@csrf_exempt
def cancel_task(request, org_id, group_id, task_id):
    if request.method == "POST":
        data = json.loads(request.body)
        reason = data.get("reason", "").strip()
        
        task = get_object_or_404(Task, id=task_id, organization_id=org_id, group_id=group_id)
        
        if task.assigned_to != request.user:
            return JsonResponse({"success": False, "message": "You are not authorized to cancel this task."}, status=403)

        created_by_email = task.created_by.email
        task_title = task.title
        organization = task.organization.name
        group = task.group.name

        # Send email notification
        send_mail(
            subject=f"Task '{task_title}' Canceled",
            message=f"Hello {task.created_by.get_full_name()},\n\n"
                    f"The task '{task_title}' in the group '{group}' under '{organization}' has been canceled by {task.assigned_to.username}.\n"
                    f"Reason for cancellation: {reason}\n\n"
                    f"Best,\nCalendar Plus Team",
            from_email="no-reply@calendarplus.com",
            recipient_list=[created_by_email]
        )

        # Delete task
        task.delete()

        return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=400)



# CREATE SUBTASK FOR THE TASK
@check_org_membership
@csrf_exempt
@login_required
def create_subtask(request, org_id, group_id, task_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # Fetch organization, group, and task
            organization = get_object_or_404(Organization, id=org_id)
            group = get_object_or_404(Group, id=group_id, organization=organization)
            task = get_object_or_404(Task, id=task_id, group=group, organization=organization)

            # Extract subtask details
            title = data.get("title")
            description = data.get("description", "")
            priority = data.get("priority", "medium")
            deadline = data.get("deadline")

            if not title or not deadline:
                return JsonResponse({"error": "Title and deadline are required."}, status=400)

            # Create subtask
            subtask = SubTask.objects.create(
                organization=organization,
                group=group,
                task=task,
                created_by=request.user,
                title=title,
                description=description,
                priority=priority,
                deadline=deadline
            )

            return JsonResponse({
                "message": "Subtask created successfully!",
                "subtask_id": subtask.id,
                "title": subtask.title,
                "priority": subtask.priority
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data."}, status=400)

    return JsonResponse({"error": "Invalid request method."}, status=405)

# MANAGE SUBTASKS
@csrf_exempt
@check_org_membership
def fetch_subtasks(request, org_id, group_id, task_id):
    task = get_object_or_404(Task, id=task_id, group_id=group_id, organization_id=org_id)
    subtasks = SubTask.objects.filter(task=task).values("id", "title", "status", "progress")

    return JsonResponse({"subtasks": list(subtasks)}, safe=False)

# Update the subtask
@csrf_exempt
@login_required
@check_org_membership
def update_subtask(request, org_id, group_id, task_id, subtask_id):
    if request.method == "POST":
        data = json.loads(request.body)
        subtask = get_object_or_404(SubTask, id=subtask_id, task_id=task_id)

        if "status" in data:
            subtask.status = data["status"]
        
        if "progress" in data:
            subtask.progress = max(0, min(100, subtask.progress + data["progress"]))  # Increment/Decrement

        subtask.save()
        return JsonResponse({"message": "SubTask updated successfully!", "new_progress": subtask.progress})

    return JsonResponse({"error": "Invalid request"}, status=400)


# delete the subtask
@check_org_membership
@csrf_exempt
def delete_subtask(request, org_id, group_id, task_id, subtask_id):
    if request.method == "POST":
        subtask = get_object_or_404(SubTask, id=subtask_id, task_id=task_id)
        subtask.delete()
        return JsonResponse({"message": "SubTask deleted successfully!"})

    return JsonResponse({"error": "Invalid request"}, status=400)


# EXPORT THE TASK DATA


@check_org_membership
@csrf_exempt
@login_required
def export_task_data(request, org_id, group_id, task_id):
    """Send Task Report as a Styled HTML Email"""
    action = request.GET.get("action") 
    user_email = request.user.email

    # ✅ Fetch Task Data
    task = get_object_or_404(Task, id=task_id, organization_id=org_id, group_id=group_id)
    subtasks = SubTask.objects.filter(task=task)
    activity_logs = ActivityLog.objects.filter(task=task)
    problems = Problem.objects.filter(task=task)
    time = TaskTimeTracking.objects.filter(task=task)


    html_content = render_to_string('task/task_report.html', {
        'task': task,
        'subtasks': subtasks,
        'activity_logs': activity_logs,
        'problems': problems,
        'time': time,
    })

    
    html_content = transform(html_content)  

    # ✅ Plain Text Fallback
    plain_text = strip_tags(html_content)


    send_mail(
        subject="Your Task Report",
        message=plain_text, 
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        html_message=html_content,  
    )

    return JsonResponse({"message": "Task report sent to your email with proper styling!"})


# ATTACHE THE ATTACHEMENT TO THE TASK (PREMIUM)
@csrf_exempt
@login_required
@check_org_membership
def attach_task_file(request, org_id, group_id, task_id):
    """Attach a file to a task and optionally send it to the manager"""

    if request.method != "POST":
        return JsonResponse({"error": "Only POST requests allowed!"}, status=400)

    task = get_object_or_404(Task, id=task_id, organization_id=org_id, group_id=group_id)

    # ✅ Get uploaded file
    uploaded_file = request.FILES.get("attachment")
    name = request.POST.get("name", uploaded_file.name)  # Default to file name
    description = request.POST.get("description", "")
    category = request.POST.get("category", AttachmentsTasksApp.FileCategory.OTHER)  
    tags = request.POST.get("tags", "")
    is_private = request.POST.get("is_private") == "true"
    send_copy_to_manager = request.POST.get("send_copy_to_manager") == "true"

    if not uploaded_file:
        return JsonResponse({"error": "No file uploaded!"}, status=400)

    # ✅ Handle file versioning
    existing_attachment = AttachmentsTasksApp.objects.filter(task=task, name=name).order_by("-version").first()
    new_version = existing_attachment.version + 1 if existing_attachment else 1

    # ✅ Save attachment
    attachment = AttachmentsTasksApp.objects.create(
        organization=task.organization,
        group=task.group,
        task=task,
        user=request.user,
        name=name,
        description=description,
        category=category,
        attachment=uploaded_file,
        version=new_version,
        tags=tags,
        is_private=is_private,
        send_copy_to_manager=send_copy_to_manager,
    )

    # ✅ If send_copy_to_manager is True, send email to the task creator
    if send_copy_to_manager and task.created_by:
        subject = f"New Attachment Added to Task: {task.title}"
        body = f"""
        Hi {task.created_by.get_full_name()},

        A new attachment has been added by {request.user.username} to the task: **{task.title}**.

        **Attachment Name:** {attachment.name}  
        **Attached By:** {request.user}  
        **Category:** {attachment.get_category_display()}  
        **Tags:** {attachment.tags or 'None'}  
        **Task Details:** {task.description or 'No description provided.'}  

        You can view the task in your dashboard.

        Best,  
        Calendar Plus Team
        """

        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[task.created_by.email],
        )

        email.attach(attachment.name, attachment.attachment.read(), mimetypes.guess_type(attachment.attachment.name)[0] or "application/octet-stream")
        email.send()

    return JsonResponse({
        "message": "Attachment added successfully!",
        "attachment_id": attachment.id,
        "version": attachment.version,
        "download_count": attachment.download_count,
    })



# FETCH FILES ATTACHED TO THE TASK

@check_org_membership
def fetch_task_attachments(request, org_id, group_id, task_id):
    """Fetch all attachments for a specific task"""
    attachments = AttachmentsTasksApp.objects.filter(
        organization_id=org_id,
        group_id=group_id,
        task_id=task_id,
        is_deleted=False  
    ).order_by("-attached_at")

    attachment_data = []
    for attachment in attachments:
        attachment_data.append({
            "id": attachment.id,
            "name": attachment.name,
            "description": attachment.description,
            "category": attachment.get_category_display(),
            "file_url": attachment.attachment.url,
            "uploaded_by": attachment.user.get_full_name(),
            "attached_at": attachment.attached_at.strftime("%Y-%m-%d %H:%M"),
            "download_count": attachment.download_count,
        })

    return JsonResponse({"attachments": attachment_data}, safe=False)

# DELETE THE ATTACHMENTS
@csrf_exempt
@login_required
@check_org_membership
def delete_task_attachment(request, org_id, group_id, task_id, attachment_id):
    """Soft delete a task attachment"""
    attachment = get_object_or_404(
        AttachmentsTasksApp,
        id=attachment_id,
        organization_id=org_id,
        group_id=group_id,
        task_id=task_id,
        is_deleted=False  # ✅ Ensure it's not already deleted
    )

    # ✅ Only allow the uploader or an admin to delete
    if request.user != attachment.user and not request.user.is_superuser:
        return JsonResponse({"error": "Permission denied!"}, status=403)

    attachment.is_deleted = True
    attachment.save()

    return JsonResponse({"message": "Attachment deleted successfully!"})


# RETRY THE ATTACHMENT
@csrf_exempt
@login_required
@check_org_membership
def retry_task_attachment(request, org_id, group_id, task_id, attachment_id):
    """Send the task attachment to the task creator via email without reassigning it."""
    
    # ✅ Fetch the attachment
    attachment = get_object_or_404(
        AttachmentsTasksApp,
        id=attachment_id,
        organization_id=org_id,
        group_id=group_id,
        task_id=task_id,
        is_deleted=False
    )

    # ✅ Fetch related models
    task = get_object_or_404(Task, id=task_id, organization_id=org_id, group_id=group_id)
    organization = get_object_or_404(Organization, id=org_id)
    group = get_object_or_404(Group, id=group_id)

    # ✅ Ensure task creator exists
    task_creator = task.created_by  
    if not task_creator or not task_creator.email:
        return JsonResponse({"error": "Task creator not found or email missing!"}, status=400)

    # ✅ Prepare email details
    subject = f"📌 New Task Attachment for '{task.title}'"
    message = f"""
    Hello {task_creator.get_full_name()},

    You have received a new attachment for your task **{task.title}**.

    🔹 **Organization:** {organization.name}  
    🔹 **Group:** {group.name}  
    🔹 **Task:** {task.title}  
    🔹 **Attachment Name:** {attachment.name}  
    🔹 **Category:** {attachment.get_category_display()}  

    Click the link below to download the attachment:  
    {request.build_absolute_uri(attachment.attachment.url)}

    Best Regards,  
    Calendar Plus Team
    """

    # ✅ Send email without reassigning the attachment
    email = EmailMessage(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [task_creator.email],
    )

    # ✅ No file attachment, just send the email
    email.send()

    return JsonResponse({"message": "Attachment successfully sent again to the manager!"})



# SEND CUSTOM QUERY ABOUT THE TASK TO THE MANAGER
@csrf_exempt
@check_org_membership
@login_required
def send_task_email(request, org_id, group_id, task_id):
    """Allows the assigned user to send a custom email to the task creator."""
    
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)
        email_subject = data.get("subject", "").strip()
        email_body = data.get("message", "").strip()
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({"error": "Invalid JSON data"}, status=400)

    if not email_subject or not email_body:
        return JsonResponse({"error": "Subject and message cannot be empty"}, status=400)

    # ✅ Fetch Task, Organization, and Group
    task = get_object_or_404(Task, id=task_id, organization_id=org_id, group_id=group_id,assigned_to=request.user)
    organization = get_object_or_404(Organization, id=org_id)
    group = get_object_or_404(Group, id=group_id)

    # ✅ Ensure the current user is assigned to the task
    current_user = request.user
    if current_user != task.assigned_to:
        return JsonResponse({"error": "You are not assigned to this task!"}, status=403)

    # ✅ Get Task Creator
    task_creator = task.created_by
    if not task_creator or not task_creator.email:
        return JsonResponse({"error": "Task creator email not found!"}, status=400)
    
    # limit on queries
    if task.queries_sent >= 45:
        return JsonResponse({'error':'you can send only 45 queries in free plan!'}, status=400)


    # ✅ Email Content
    email_message = f"""
    Hello {task_creator.get_full_name()},

    The user **{current_user.username}** working on your task **"{task.title}"** has sent you a message.

    📌 **Task Details:**
    - **Organization:** {organization.name}
    - **Group:** {group.name}
    - **Task:** {task.title}

    📩 **Message from {current_user.username}:**  
    {email_body}

    Best Regards,  
    Calendar Plus Team
    """

    # ✅ Send Email
    send_mail(
        subject=email_subject,
        message=email_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[task_creator.email],
        fail_silently=False,
    )
    # increment the count of queries
    task.queries_sent+=1
    task.save()

    
    return JsonResponse({"message": "Email successfully sent to the task creator!"})


# SCHEDULE THE MEETING FOR TASK (PREMIUM)
from datetime import datetime, timedelta
from accounts.models import Availability,MeetingOrganization

@login_required
def get_available_slots(request):
    org_id = request.GET.get("org_id")
    group_id = request.GET.get("group_id")
    task_id = request.GET.get("task_id")
    date_str = request.GET.get("date")  # Expected format: YYYY-MM-DD

    profile = get_object_or_404(Profile, user=request.user, organization_id=org_id)
    if not profile:
        return JsonResponse({'error:':'you are not authorized to access this!'},status=400)


    if not all([org_id, group_id, task_id, date_str]):
        return JsonResponse({"error": "Missing required parameters"}, status=400)

    # Parse date
    try:
        selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse({"error": "Invalid date format"}, status=400)

    # Get Task & Task Creator
    task = get_object_or_404(Task, id=task_id)
    task_creator = task.created_by

    # Fetch Availability for Task Creator (Filtered by Organization)
    availability = Availability.objects.filter(
        user=task_creator, organization_id=org_id, day_of_week=selected_date.weekday()
    )

    # Fetch Meetings where Task Creator is either `user` or `invitee`
    meetings = MeetingOrganization.objects.filter(
        organization_id=org_id, meeting_date=selected_date
    ).filter(user=task_creator) | MeetingOrganization.objects.filter(invitee=task_creator)

    # Fetch `MeetingTaskQuery` bookings for Task Creator
    task_meetings = MeetingTaskQuery.objects.filter(
        organization_id=org_id, date=selected_date, task_creator=task_creator
    )

    # Create list of booked time slots
    booked_slots = set()  # Use a set for fast lookups

    # Process booked slots from `MeetingOrganization`
    for meeting in meetings:
        start = datetime.combine(selected_date, meeting.start_time)
        end = datetime.combine(selected_date, meeting.end_time)
        while start < end:
            booked_slots.add(start.time())
            start += timedelta(minutes=30)

    # Process booked slots from `MeetingTaskQuery`
    for task_meeting in task_meetings:
        start = task_meeting.start_time.time()  # Convert DateTime to Time
        end = task_meeting.end_time.time()
        current_time = datetime.combine(selected_date, start)

        while current_time.time() < end:
            booked_slots.add(current_time.time())
            current_time += timedelta(minutes=30)

    # Generate 30-minute slots from availability
    available_slots = []
    for slot in availability:
        current_time = datetime.combine(selected_date, slot.start_time)
        end_time = datetime.combine(selected_date, slot.end_time)
        
        while current_time + timedelta(minutes=30) <= end_time:
            if current_time.time() not in booked_slots:
                available_slots.append(
                    {"start_time": current_time.time().strftime("%H:%M")}
                )
            current_time += timedelta(minutes=30)

    return JsonResponse({"available_slots": available_slots})


# -------------------------------------------------------------------------------------------------------------------------working on it ------------
# SCHEDULE THE MEETING
from django.utils.timezone import make_aware
from django.db.models import Q
import random
import string


# generate google meeting link
def generate_meet_link():
    """Creates a Google Meet-style link without authentication."""
    random_code = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
    return f"https://meet.google.com/{random_code}"


@csrf_exempt 
def schedule_meeting(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=400)

    try:
        data = json.loads(request.body)
        org_id = data.get("org_id")
        group_id = data.get("group_id")
        task_id = data.get("task_id")
        date_str = data.get("date")  # Expected format: YYYY-MM-DD
        start_time_str = data.get("start_time")  # Expected format: HH:MM
        reason = data.get("reason")

        profile = get_object_or_404(Profile, user=request.user, organization_id=org_id)
        if not profile:
            return JsonResponse({'error:':'you are not authorized to access this!'},status=400)

        if not all([org_id, group_id, task_id, date_str, start_time_str, reason]):
            return JsonResponse({"error": "Missing required fields"}, status=400)

        # Convert date & time
        selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        start_time = datetime.strptime(start_time_str, "%H:%M").time()
        end_time = (datetime.combine(selected_date, start_time) + timedelta(minutes=30)).time()

        # Get Task & Task Creator
        task = get_object_or_404(Task, id=task_id)
        task_creator = task.created_by

        # Check if the selected slot is already booked
        is_booked = MeetingOrganization.objects.filter(
            Q(user=task_creator) | Q(invitee=task_creator),
            organization_id=org_id,
            meeting_date=selected_date,
            start_time__lt=end_time,
            end_time__gt=start_time,
        ).exists()

        if is_booked:
            return JsonResponse({"error": "Selected time slot is no longer available"}, status=400)

        # Schedule Meeting
        meeting = MeetingTaskQuery.objects.create(
            organization_id=org_id,
            group_id=group_id,
            task_id=task_id,
            scheduled_by=request.user,  
            task_creator=task_creator,
            date=selected_date,
            start_time=make_aware(datetime.combine(selected_date, start_time)),
            end_time=make_aware(datetime.combine(selected_date, end_time)),
            reason=reason,
            status="pending",
            meeting_link=generate_meet_link(),
        )

        return JsonResponse({"success": "Meeting scheduled successfully", "meeting_id": meeting.id})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# GET EXISTING MEETINGS
def get_existing_meetings(request):
    org_id = request.GET.get("org_id")
    group_id = request.GET.get("group_id")
    task_id = request.GET.get("task_id")

    profile = get_object_or_404(Profile, user=request.user, organization_id=org_id)
    if not profile:
        return JsonResponse({'error:':'You are not authorized to access this page!'},status=400)

    if not all([org_id, group_id, task_id]):
        return JsonResponse({"error": "Missing required parameters"}, status=400)

    # Fetch existing meetings for the task
    meetings = MeetingTaskQuery.objects.filter(
        organization_id=org_id,
        group_id=group_id,
        task_id=task_id
    ).values(
        "id", "date", "start_time", "end_time", "reason", "status",'meeting_link',
    )

    # Format the response
    meeting_list = []
    for meeting in meetings:
        meeting_list.append({
            "id": meeting["id"],
            "date": meeting["date"].strftime("%Y-%m-%d"),
            "start_time": meeting["start_time"].strftime("%H:%M"),
            "end_time": meeting["end_time"].strftime("%H:%M"),
            "reason": meeting["reason"],
            "status": meeting["status"],
            'meeting_link':meeting['meeting_link'],
        })

    return JsonResponse({"meetings": meeting_list})


# MANAGER SIDE VIEW (FETCH MEETINGS)

@login_required
def fetch_task_meetings(request):
    """Fetch all meetings related to a specific Task."""
    if request.method != "GET":
        return JsonResponse({"error": "Invalid request method"}, status=400)

    org_id = request.GET.get("org_id")
    group_id = request.GET.get("group_id")
    task_id = request.GET.get("task_id")

    task=get_object_or_404(Task, id=task_id, organization_id=org_id,created_by=request.user)

    if request.user != task.created_by:
        return JsonResponse({'error:':'you are the manager ! couldnt process your request!'}, status=400)

    profile = get_object_or_404(Profile, user=request.user, organization_id=org_id)
    if not profile:
        return JsonResponse({'error:':'you are not authorized to access this!'},status=400)


    if not all([org_id, group_id, task_id]):
        return JsonResponse({"error": "Missing required parameters"}, status=400)

    # Get all meetings related to the Task
    meetings = MeetingTaskQuery.objects.filter(
        organization_id=org_id,
        group_id=group_id,
        task_id=task_id,
    ).select_related("task_creator", "scheduled_by")  # Optimize DB queries

    # Format response
    meetings_data = [
        {
            "id": meeting.id,
            "date": meeting.date.strftime("%Y-%m-%d"),
            "start_time": meeting.start_time.strftime("%H:%M"),
            "end_time": meeting.end_time.strftime("%H:%M"),
            "reason": meeting.reason,
            "status": meeting.status,
            "meeting_link": meeting.meeting_link,
            "scheduled_by": meeting.scheduled_by.username if meeting.scheduled_by else "Unknown",
            "task_creator": meeting.task_creator.username if meeting.task_creator else "Unknown",
        }
        for meeting in meetings
    ]

    return JsonResponse({"meetings": meetings_data}, status=200)


# UPDATE THE MEETING STATUS
@csrf_exempt
@login_required
def update_meeting_status(request):
    """Allows task.creator to update the status of a meeting."""
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=400)

    try:
        data = json.loads(request.body)
        meeting_id = data.get("meeting_id")
        new_status = data.get("status")

        if not all([meeting_id, new_status]):
            return JsonResponse({"error": "Missing required fields"}, status=400)

        # Get the meeting
        meeting = get_object_or_404(MeetingTaskQuery, id=meeting_id,task_creator=request.user)

        profile= get_object_or_404(Profile, user=request.user,organization=meeting.organization)
        if not profile:
            return JsonResponse({'error:':'you are not authorized to access this page!'}, status=400)

        # Check if the requester is the task creator
        if request.user != meeting.task_creator:
            return JsonResponse({"error": "Unauthorized"}, status=403)

        # Update the status
        meeting.status = new_status
        meeting.save()

        return JsonResponse({"success": "Meeting status updated successfully!"}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# SPECIFIC ROOM FOR MANAGER AND THE TASK ACCOMPLISHER
@check_org_membership
@login_required
def fetch_task_messages(request, org_id, group_id, task_id):
    if request.method == "GET":
        organization = get_object_or_404(Organization, id=org_id)
        group = get_object_or_404(Group, id=group_id,organization=organization)
        task = get_object_or_404(Task, id=task_id,group=group,organization=organization)

        if not task and group and organization:
            return JsonResponse({'error':'something went really wrong!'},status=400)

        messages = CommunicateTask.objects.filter(
            organization=organization, group=group, task=task
        ).order_by("-id")

        data = [
            {
                "id": msg.id,
                "message": msg.message,
                "file": msg.files.url if msg.files else None,
                "sender": msg.sender.username,
                "created_at": msg.id,  # Modify if you want a formatted timestamp
                 "profile": (
                    msg.sender.profiles.filter(organization=organization).first().profile_picture.url 
                    if msg.sender.profiles.filter(organization=organization).exists() and msg.sender.profiles.filter(organization=organization).first().profile_picture 
                  else "No URL")
            }
            for msg in messages
        ]
        return JsonResponse({"messages": data}, safe=False)

# send messages 
@csrf_exempt
@login_required
def send_task_message(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Parse JSON data

            task_id = data.get("task_id")
            org_id = data.get("org_id")
            group_id = data.get("group_id")
            message = data.get("message", "")
            file_data = data.get("file", None)  # Base64 file data
            file_name = data.get("file_name", None)  # File name

            task = get_object_or_404(Task, id=task_id)
            organization = get_object_or_404(Organization, id=org_id)
            group = get_object_or_404(Group, id=group_id)
            sender = request.user

            profile=get_object_or_404(Profile,user=request.user,organization=organization)
            if not profile:
                return JsonResponse({'error:':'you are not authorized!'},status=400)

            # Handle file saving
            file_obj = None
            if file_data and file_name:
                format, file_str = file_data.split(";base64,")
                ext = file_name.split(".")[-1]
                file_obj = ContentFile(base64.b64decode(file_str), name=f"task_files/{file_name}")

            communicate_task = CommunicateTask.objects.create(
                task=task, organization=organization, group=group,
                message=message, files=file_obj, sender=sender
            )

            return JsonResponse({
                "success": True,
                "message": "Message sent successfully!",
                "data": {
                    "id": communicate_task.id,
                    "message": communicate_task.message,
                    "file": communicate_task.files.url if communicate_task.files else None,
                    "sender": communicate_task.sender.username,
                    "created_at": communicate_task.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                }
            })

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON data"}, status=400)

    return JsonResponse({"success": False, "error": "Invalid request method"}, status=405)


# delete the message
@csrf_exempt
@login_required
@check_org_membership
def delete_all_task_messages(request, org_id, group_id, task_id):
    if request.method == "DELETE":
        try:
            # Delete all messages for the given task
            CommunicateTask.objects.filter(task_id=task_id, group_id=group_id, organization_id=org_id,sender=request.user).delete()
            return JsonResponse({"success": True, "message": "All messages deleted successfully."})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
    
    return JsonResponse({"success": False, "error": "Invalid request method."}, status=400)

# EXPORT THE CHAT DATA


@check_org_membership
@login_required
def export_task_chat(request, org_id, group_id, task_id):

    organization=get_object_or_404(Organization,id=org_id)
    group=get_object_or_404(Group, id=group_id)
    task=get_object_or_404(Task,id=task_id)

    # Fetch messages related to the task
    messages = CommunicateTask.objects.filter(task_id=task_id, group_id=group_id, organization_id=org_id).order_by("created_at")

    # Create PDF response
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="task_chat_{task_id}.pdf"'

    # Generate PDF using ReportLab
    pdf = canvas.Canvas(response, pagesize=letter)
    pdf.setTitle(f"Chat Export - Task {task_id}")

    # PDF Title
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(200, 750, f"Chat Messages for Task {task.title} - Group: {group.name}")
    
    y_position = 730
    pdf.setFont("Helvetica", 10)

    if messages.exists():
        for msg in messages:
            # Format message content
            message_text = f"{msg.sender.username}: {msg.message}  ({msg.created_at.strftime('%Y-%m-%d %H:%M')})"

            pdf.drawString(50, y_position, message_text)
            y_position -= 20

            # If there is a file, add a reference
            if msg.files:
                pdf.drawString(50, y_position, f"🔗 File: {msg.files.url}")
                y_position -= 20

            # Page handling
            if y_position < 50:
                pdf.showPage()
                pdf.setFont("Helvetica", 10)
                y_position = 750
    else:
        pdf.drawString(50, y_position, "No messages available for this task.")

    pdf.save()
    return response


# RETURN TASKS SUBTASKS TO THE MANAGER
@check_org_membership
@login_required
def get_task_subtasks(request, org_id, group_id, task_id):
    """
    Retrieves a task's details and its subtasks, ensuring that only the task creator can view them.
    """
    task = get_object_or_404(Task, id=task_id, organization_id=org_id, group_id=group_id)

    # Check if the current user is the creator of the task
    if request.user != task.created_by:
        return JsonResponse({"error": "Permission denied"}, status=403)

    # Retrieve all subtasks under this task
    subtasks = SubTask.objects.filter(task=task).values(
        "id", "title", "description", "priority", "status", "progress", "deadline", "created_at"
    )

    # Prepare response data
    data = {
        "task": {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "progress": task.progress,
            "status": task.status,
        },
        "subtasks": list(subtasks)
    }

    return JsonResponse(data)


# MANAGER (ASSIGN THE SUBTASKS)
@csrf_exempt
@check_org_membership
@login_required
def assign_subtask(request, org_id, group_id, task_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            title = data.get("title")
            description = data.get("description", "")
            priority = data.get("priority", "medium")
            deadline = data.get("deadline")
            remind_before_due_date = data.get("remind_before_due_date", "never")

            # New fields
            delete_after_completion = data.get("delete_after_completion", False)
            can_edit_task = data.get("can_edit_task", False)
            behaviour = data.get("behaviour", None)

            # Validate input
            if not title or not deadline:
                return JsonResponse({"error": "Title and deadline are required."}, status=400)

            # Fetch related objects
            organization = get_object_or_404(Organization, id=org_id)
            group = get_object_or_404(Group, id=group_id)
            task = get_object_or_404(Task, id=task_id)

            # Create the subtask
            subtask = SubTask.objects.create(
                organization=organization,
                group=group,
                task=task,
                created_by=task.assigned_to,
                title=title,
                description=description,
                priority=priority,
                deadline=deadline,
                status="pending",
                progress=0,
                remind_before_due_date=remind_before_due_date,
                delete_after_completion=delete_after_completion,
                can_edit_task=can_edit_task,
                behaviour=behaviour,
            )

            # notify subtask user
            notify_subtask_user(org_id=organization.id,group_id=group.id,task_id=task.id,subtask_id=subtask.id)

            return JsonResponse(
                {
                    "message": "Subtask assigned successfully!",
                    "subtask_id": subtask.id,
                    "reminder": remind_before_due_date,
                    "delete_after_completion": delete_after_completion,
                    "can_edit_task": can_edit_task,
                    "behaviour": behaviour,
                },
                status=201
            )

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data."}, status=400)

    return JsonResponse({"error": "Invalid request method."}, status=405)

# notify the task accomplisher
def notify_subtask_user(org_id,group_id,task_id,subtask_id):
    organization=get_object_or_404(Organization,id=org_id)
    group=get_object_or_404(Group, id=group_id,organization=organization)
    task=get_object_or_404(Task, id=task_id, group=group, organization=organization)
    subtask = get_object_or_404(SubTask, id=subtask_id, task=task, group=group, organization=organization)

    subject=f"New Subtask Assigned to {task.title}"
    message=f'Hello {task.assigned_to.username}, {task.created_by.username} assigned a subtask to the {task.title}, Here are the subtask details below!\n Title: {subtask.title}\n Priority: {subtask.priority}\n Deadline: {subtask.deadline}\n Workspace And Group Details: Workspace: {organization.name}\n Group:{group.name}\n Kindly complete the task before {subtask.deadline} to avoid any due issues'
    from_email=settings.DEFAULT_FROM_EMAIL
    recipient_list = [task.assigned_to.email]

    send_mail(subject, message, from_email, recipient_list)


# CLONE AND ASSIGN THE TASK
@csrf_exempt
def clone_task(request):
    if request.method == "POST":
        try:
            # Debugging: Print the raw request body
            print("🔍 Raw Request Body:", request.body)

            # Parse JSON data
            data = json.loads(request.body)
            print("📌 Parsed JSON Data:", data)

            org_id = data.get("org_id")
            group_id = data.get("group_id")
            task_id = data.get("task_id")
            email = data.get("email")

            # Debugging: Print extracted values
            print(f"✅ Extracted Data - org_id: {org_id}, group_id: {group_id}, task_id: {task_id}, email: {email}")

            # security check manual
            profile= get_object_or_404(Profile,user=request.user, organization_id=org_id)
            if not profile:
              return JsonResponse({'error:':'You are not authorized to perform this action'})


            # Validate required fields
            if not all([org_id, group_id, task_id, email]):
                print("❌ Missing required parameters!")
                return JsonResponse({"error": "Missing required parameters."}, status=400)

            # Fetch organization & group
            organization = get_object_or_404(Organization, id=org_id)
            print(f"🏢 Organization Found: {organization}")

            group = get_object_or_404(Group, id=group_id, organization=organization)
            print(f"👥 Group Found: {group}")

            # Fetch the original task
            task = get_object_or_404(Task, id=task_id, group=group, organization=organization)
            print(f"📋 Original Task Found: {task}")

            # Find user by email inside the same organization
            profile = Profile.objects.filter(user__email=email, organization=organization).first()

            # prevent assign to admin
            if profile.is_admin:
                return JsonResponse({'error:':'You cant assign the task to the workspace admin!'}, status=400)

            if not profile:
                print(f"❌ No profile found for email: {email} in organization {organization}")
                return JsonResponse({"error": "User with this email not found in the organization."}, status=404)

            user = profile.user  # Get the user from the profile
            print(f"👤 User Found: {user}")

            # Clone the task
            cloned_task = Task.objects.create(
                organization=organization,
                group=group,
                created_by=task.created_by,  # Keep the original creator
                assigned_to=user,  # Assign to new user
                title=task.title,
                description=task.description,
                priority=task.priority,
                status=task.status,
                deadline=task.deadline,
                start_date=task.start_date,
                end_date=task.end_date,
                progress=task.progress,
                is_recurring=task.is_recurring,
                recurrence_pattern=task.recurrence_pattern,
                recurrence_end_date=task.recurrence_end_date,
                notify_assignee=task.notify_assignee,
                is_urgent_notification_sent=False,  # Reset urgent notification flag
                queries_sent=0  # Reset queries count
            )
            # notify the task cloned
            notify_task_cloned(org_id=organization.id, group_id=group.id, task_id=task.id)

            print(f"✅ Task Cloned Successfully! New Task ID: {cloned_task.id}")

            return JsonResponse({"success": "Task cloned successfully.", "task_id": cloned_task.id}, status=200)

        except json.JSONDecodeError as e:
            print(f"❌ JSON Decode Error: {e}")
            return JsonResponse({"error": "Invalid JSON data."}, status=400)
        except ObjectDoesNotExist as e:
            print(f"❌ Object Not Found: {e}")
            return JsonResponse({"error": "Requested resource not found."}, status=404)
        except Exception as e:
            print(f"❌ Unexpected Error: {e}")
            return JsonResponse({"error": "An error occurred while cloning the task.", "details": str(e)}, status=500)

    print("❌ Invalid request method (Only POST allowed)")
    return JsonResponse({"error": "Invalid request method."}, status=405)


# Notify the cloned task user (task.assigned_to)
from django.core.mail import send_mail, EmailMultiAlternatives
import logging

# Set up logger
logger = logging.getLogger(__name__)

def notify_task_cloned(org_id, group_id, task_id):
    try:
        # Fetch required objects
        organization = get_object_or_404(Organization, id=org_id)
        group = get_object_or_404(Group, id=group_id, organization=organization)
        task = get_object_or_404(Task, id=task_id, group=group, organization=organization)

       
        # Ensure task has an assignee
        if not task.assigned_to or not task.assigned_to.email:
            logger.warning(f"Task {task_id} has no valid assignee. Skipping email notification.")
            return
        
        # Email Details
        subject = f'📌 New Task Assigned: {task.title}'
        recipient_email = task.assigned_to.email

        # Construct Message
        message_text = f"""Hey {task.assigned_to.username},

{task.created_by} assigned a new task to you! Check out the details:

📂 **Workspace & Group**  
- **Workspace**: {organization.name}  
- **Group**: {group.name}  

📝 **Task Details**  
- **Title**: {task.title}  
- **Description**: {task.description or 'No description provided'}  
- **Priority**: {task.priority}  
- **Deadline**: {task.deadline.strftime('%Y-%m-%d %H:%M') if task.deadline else 'No deadline set'}  

🔗 **Login to your Dashboard to get started!**  

Best,  
🚀 Team CalendarPlus  
        """

        # HTML Email Version
        message_html = f"""
        <p>Hey <strong>{task.assigned_to.username}</strong>,</p>
        <p><strong>{task.created_by}</strong> assigned a new task to you! Check out the details below:</p>

        <h3>📂 Workspace & Group</h3>
        <ul>
            <li><strong>Workspace:</strong> {organization.name}</li>
            <li><strong>Group:</strong> {group.name}</li>
        </ul>

        <h3>📝 Task Details</h3>
        <ul>
            <li><strong>Title:</strong> {task.title}</li>
            <li><strong>Description:</strong> {task.description or 'No description provided'}</li>
            <li><strong>Priority:</strong> {task.priority}</li>
            <li><strong>Deadline:</strong> {task.deadline.strftime('%Y-%m-%d %H:%M') if task.deadline else 'No deadline set'}</li>
        </ul>

        <p>🔗 <a href="{settings.SITE_URL}/dashboard/">Login to your Dashboard</a> to get started!</p>

        <p>Best,<br>🚀 <strong>Team CalendarPlus</strong></p>
        """

        # Create email object
        email = EmailMultiAlternatives(
            subject=subject,
            body=strip_tags(message_html),  # Fallback to plain text
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email]
        )
        email.attach_alternative(message_html, "text/html")  # Attach HTML version

        # Send email asynchronously
        email.send(fail_silently=False)
        logger.info(f"✅ Task notification sent successfully to {recipient_email}")

    except Exception as e:
        logger.error(f"❌ Error in notify_task_cloned: {str(e)}")


# FETCH TASK RELATED MEETINGS (sortable.js (drag&drop))
# ✅ 1️⃣ Fetch Meetings for a Specific Task
@login_required
def fetch_meetings_sortable(request, org_id, group_id, task_id):
    # Ensure task exists in the given organization & group
    task = get_object_or_404(Task, id=task_id, group_id=group_id, organization_id=org_id)

    # Fetch meetings related to this specific task
    meetings = MeetingTaskQuery.objects.filter(organization_id=org_id, group_id=group_id, task_id=task_id)

    # security check manual
    profile= get_object_or_404(Profile,user=request.user, organization=task.organization)
    if not profile:
        return JsonResponse({'error:':'You are not authorized to perform this action'})


    meetings_data = [
        {
            "id": meeting.id,
            "task_title": meeting.task.title,
            "scheduled_by": meeting.scheduled_by.username,
            "task_creator": meeting.task_creator.username,
            "date": meeting.date.strftime("%Y-%m-%d") if meeting.date else "Not Scheduled",
            "start_time": meeting.start_time.strftime("%H:%M"),
            "end_time": meeting.end_time.strftime("%H:%M"),
            "reason": meeting.get_reason_display(),
            "status": meeting.status,
            "meeting_link": meeting.meeting_link if meeting.meeting_link else "#",
        }
        for meeting in meetings
    ]

    return JsonResponse({"meetings": meetings_data}, status=200)


# UPDATE THE MEETING STATUS
# ✅ 2️⃣ Handle Status Update
@login_required
@csrf_exempt
def update_meeting_status_sortable(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Parse JSON data from request body
            print("recieved data:",data)
            meeting_id = data.get("meeting_id")
            new_status = data.get("new_status")

            # Validate input
            if not meeting_id or new_status not in ["pending", "confirmed", "cancelled"]:
                return JsonResponse({"error": "Invalid request data."}, status=400)

            # Fetch meeting object
            meeting = get_object_or_404(MeetingTaskQuery, id=meeting_id)

            # security check manual
            profile= get_object_or_404(Profile,user=request.user, organization=meeting.organization)
            if not profile:
              return JsonResponse({'error:':'You are not authorized to perform this action'})


            # Check if the user is the task creator
            if request.user != meeting.task.created_by:
                return JsonResponse({"error": "Unauthorized action."}, status=403)

            # Update status
            meeting.status = new_status
            meeting.save()

            return JsonResponse({"success": "Meeting status updated successfully.", "new_status": new_status}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data."}, status=400)

    return JsonResponse({"error": "Invalid request method."}, status=405)

# GET MEETING DETAILS 
@login_required
def get_meeting_details(request, meeting_id):
    meeting = get_object_or_404(MeetingTaskQuery, id=meeting_id)

    # security check manual
    profile= get_object_or_404(Profile,user=request.user, organization=meeting.organization)
    if not profile:
        return JsonResponse({'error:':'You are not authorized to perform this action'})


    data = {
        "task_title": meeting.task.title,
        "reason": meeting.reason,
        "date": meeting.date.strftime("%Y-%m-%d"),
        "start_time": meeting.start_time.strftime("%H:%M"),
        "end_time": meeting.end_time.strftime("%H:%M"),
        "status": meeting.status,
        'meeting_link':meeting.meeting_link,
    }

    return JsonResponse(data, status=200)


# HANDLE CUSTOM REPLY


@csrf_exempt
def send_custom_reply(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            meeting_id = data.get("meeting_id")
            org_id = data.get("org_id")
            task_id = data.get("task_id")
            reply_text = data.get("reply_text")

            print('RECIEVED TEXT:',reply_text)

            meeting = MeetingTaskQuery.objects.get(id=meeting_id, organization_id=org_id)
            task = Task.objects.get(id=task_id)
            organization=get_object_or_404(Organization, id=org_id)

            # security check manual
            profile= get_object_or_404(Profile,user=request.user, organization=organization)
            if not profile:
              return JsonResponse({'error:':'You are not authorized to perform this action'})


            # Here, send the reply to meeting.created_by (modify as needed)
            recipient = meeting.scheduled_by
            message = f"Custom Reply for Task '{task.title}': {reply_text}"

            # Simulate sending message (you can integrate email/notifications)
            print(f"Message sent to {recipient.email}: {message}")

            # send the email
            send_reply(org_id=organization.id, task_id=task.id, meeting_id=meeting.id, reply_text=reply_text)

            return JsonResponse({"success": True, "message": "Reply sent successfully."})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)


# SET REMINDER MEET
# logic will be pending
def set_reminder(request):
    if request.method == "POST":
        data = json.loads(request.body)
        meeting_id = data.get("meeting_id")
        org_id = data.get("org_id")
        task_id = data.get("task_id")

        # Reminder logic (Modify this as needed)
        print(f"Reminder set for Meeting {meeting_id}")

        return JsonResponse({"success": True, "message": "Reminder set successfully!"})
    return JsonResponse({"success": False, "message": "Failed to set reminder."})

# TRASH THE MEETING
@login_required
def delete_meeting(request, meeting_id):
    if request.method == "POST":
        try:
            meeting = MeetingTaskQuery.objects.get(id=meeting_id)
            # security check manual
            profile= get_object_or_404(Profile,user=request.user, organization=meeting.organization)
            if not profile:
               return JsonResponse({'error:':'You are not authorized to perform this action'})

            meeting.delete()
            return JsonResponse({"success": True, "message": "Meeting deleted successfully."})
        except MeetingOrganization.DoesNotExist:
            return JsonResponse({"success": False, "error": "Meeting not found."}, status=404)
    return JsonResponse({"success": False, "error": "Invalid request method."}, status=400)


# HANDLE THE REMINDER
from django.utils import timezone

@csrf_exempt  
def set_task_reminder(request, org_id, group_id, task_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # Fetch organization, group, and task
            organization = get_object_or_404(Organization, id=org_id)
            group = get_object_or_404(Group, id=group_id) if group_id != "null" else None
            task = get_object_or_404(Task, id=task_id, organization=organization)


            # security check manual
            profile= get_object_or_404(Profile,user=request.user, organization=organization)
            if not profile:
              return JsonResponse({'error:':'You are not authorized to perform this action'})


            # Extract Reminder Data
            reminder_time = data.get("reminder_time")
            remind_x_minutes_before = data.get("remind_x_minutes_before")
            remind_x_hours_before = data.get("remind_x_hours_before")
            remind_x_days_before = data.get("remind_x_days_before")
            remind_x_weeks_before = data.get("remind_x_weeks_before")
            remind_x_months_before = data.get("remind_x_months_before")
            remind_assignee_every_morning = data.get("remind_assignee_every_morning", False)
            remind_assignee_every_evening = data.get("remind_assignee_every_evening", False)
            remind_every_x_days = data.get("remind_every_x_days")
            remind_every_x_weeks = data.get("remind_every_x_weeks")
            remind_every_x_months = data.get("remind_every_x_months")
            snooze_until = data.get("snooze_until")
            notification_type = data.get("notification_type", "in_app")
            priority = data.get("priority", "medium")

            # Calculate Reminder Time if not provided
            if not reminder_time and task.due_date:
                if remind_x_minutes_before:
                    reminder_time = task.due_date - timedelta(minutes=int(remind_x_minutes_before))
                elif remind_x_hours_before:
                    reminder_time = task.due_date - timedelta(hours=int(remind_x_hours_before))
                elif remind_x_days_before:
                    reminder_time = task.due_date - timedelta(days=int(remind_x_days_before))
                elif remind_x_weeks_before:
                    reminder_time = task.due_date - timedelta(weeks=int(remind_x_weeks_before))
                elif remind_x_months_before:
                    reminder_time = task.due_date - timedelta(days=int(remind_x_months_before) * 30)

            # Convert reminder_time & snooze_until to datetime
            # Convert reminder_time to datetime and make it timezone-aware
            if reminder_time:
               reminder_time = timezone.make_aware(datetime.strptime(reminder_time, "%Y-%m-%dT%H:%M"))

            # Convert snooze_until to datetime and make it timezone-aware
            if snooze_until:
                snooze_until = timezone.make_aware(datetime.strptime(snooze_until, "%Y-%m-%dT%H:%M"))
            # Create Task Reminder
            reminder = TaskReminder.objects.create(
                organization=organization,
                group=group,
                task=task,
                created_by=request.user,
                reminder_time=reminder_time,
                remind_x_minutes_before=remind_x_minutes_before,
                remind_x_hours_before=remind_x_hours_before,
                remind_x_days_before=remind_x_days_before,
                remind_x_weeks_before=remind_x_weeks_before,
                remind_x_months_before=remind_x_months_before,
                remind_assignee_every_morning=remind_assignee_every_morning,
                remind_assignee_every_evening=remind_assignee_every_evening,
                remind_every_x_days=remind_every_x_days,
                remind_every_x_weeks=remind_every_x_weeks,
                remind_every_x_months=remind_every_x_months,
                snooze_until=snooze_until,
                notification_type=notification_type,
                priority=priority,
            )

            return JsonResponse({"status": "success", "message": "Reminder set successfully!", "reminder_id": reminder.id})

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status": "error", "message": "Invalid request method!"})


# HANDLE TASK DELETION (MANAGER ONLY)
from django.contrib.auth import authenticate

@login_required
@csrf_exempt
def task_delete_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  
            org_id = data.get("org_id")
            group_id = data.get("group_id")
            task_id = data.get("task_id")
            password = data.get("password")

            user = request.user
            organization = get_object_or_404(Organization, id=org_id)
            group = get_object_or_404(Group, id=group_id, organization=organization)
            task = get_object_or_404(Task, id=task_id, group=group, organization=organization)


            # security check manual
            profile= get_object_or_404(Profile,user=request.user, organization=organization)
            if not profile:
              return JsonResponse({'error:':'You are not authorized to perform this action'})


            # Ensure only the task creator can delete
            if task.created_by != user:
                return JsonResponse({"status": "error", "message": "You are not authorized to delete this task."}, status=403)

            # Authenticate user password
            if not user.check_password(password):
                return JsonResponse({"status": "error", "message": "Incorrect password. Task deletion failed."}, status=401)
            
            # notify the user about task deletion
            after_task_deletion(org_id=organization.id,group_id=group.id,task_id=task.id)

            # Delete Task
            task.delete()
            return JsonResponse({"status": "success", "message": "Task deleted successfully."})

        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON data."}, status=400)

    return JsonResponse({"status": "error", "message": "Invalid request."}, status=400)


# TASK SUBMISSION & APPROVAL

# USER (SIDE)
@csrf_exempt
@login_required
def task_completion_request_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            org_id = data.get("org_id")
            group_id = data.get("group_id")
            task_id = data.get("task_id")
            password = data.get("password")

            user = request.user
            organization = get_object_or_404(Organization, id=org_id)
            group = get_object_or_404(Group, id=group_id, organization=organization)
            task = get_object_or_404(Task, id=task_id, group=group, organization=organization)


             # security check manual
            profile= get_object_or_404(Profile,user=request.user, organization=organization)
            if not profile:
               return JsonResponse({'error:':'You are not authorized to perform this action'})


            # ✅ Ensure only the assigned user can submit task completion
            if task.assigned_to != user:
                return JsonResponse({"status": "error", "message": "You are not authorized to complete this task."}, status=403)

            # ✅ Check user password authentication
            if not user.check_password(password):
                return JsonResponse({"status": "error", "message": "Incorrect password. Task completion failed."}, status=401)

            # ✅ Send request to task.created_by for approval
            task.status = "pending_approval"
            task.save()
            # send task approval to the manager
            task_submission_approval(org_id=organization.id, group_id=group_id,task_id=task.id)

            return JsonResponse({"status": "success", "message": "Task completion request sent for approval."})

        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON data."}, status=400)

    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=400)


# MANAGER SIDE (TASK APPROVE OR REJECT)
# Pending EMail notification
@csrf_exempt
def approve_or_reject_task(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            org_id = data.get("org_id")
            group_id = data.get("group_id")
            task_id = data.get("task_id")
            password = data.get("password")
            action = data.get("action") 

            organization = get_object_or_404(Organization, id=org_id)

            # ✅ Validate Fields
            if not (org_id and group_id and task_id and password and action):
                return JsonResponse({"status": "error", "message": "Missing required fields."}, status=400)

            # ✅ Get Logged-in Manager
            user = request.user
            if not user.is_authenticated:
                return JsonResponse({"status": "error", "message": "You must be logged in."}, status=401)

            # ✅ Authenticate Password
            if not authenticate(username=user.username, password=password):
                return JsonResponse({"status": "error", "message": "Incorrect password."}, status=403)
            
            # security check manual
            profile= get_object_or_404(Profile,user=request.user, organization_id=org_id)
            if not profile:
               return JsonResponse({'error:':'You are not authorized to perform this action'})


            # ✅ Get Task
            try:
                task = Task.objects.get(id=task_id, group_id=group_id, organization_id=org_id)
            except Task.DoesNotExist:
                return JsonResponse({"status": "error", "message": "Task not found."}, status=404)

            # ✅ Approve Task
            if action == "approve":
                if task.status == "completed":
                    return JsonResponse({"status": "error", "message": "Task is already completed."}, status=400)

                task.status = "completed"
                task.save()

                # Save the unseen info 
                PendingRewardNotification.objects.create(
                    task=task,
                    organization=organization,
                    group=task.group,
                    user=task.assigned_to,

                )
                # 💌 Send Email Notification with Organization & Group Details
                send_task_notification_email(org_id, group_id, task_id, "approve")
    
                return JsonResponse({"status": "success", "message": "Task has been approved & completed!", "approved": True}, status=200)

            # ❌ Reject Task
            elif action == "reject":
                task.status = "need_changes"
                task.progress=50
                task.save()
                # 💌 Send Email Notification with Organization & Group Details
                send_task_notification_email(org_id, group_id, task_id, "reject")
    
                return JsonResponse({"status": "success", "message": "Task has been rejected & set to Need Changes!", "approved": False}, status=200)

            return JsonResponse({"status": "error", "message": "Invalid action."}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON format."}, status=400)

    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)






# Share the task with team members
def get_workspace_members(request):
    """Fetch all members of an organization with full profile picture URLs."""
    org_id = request.GET.get("org_id")
    
    if not org_id:
        return JsonResponse({"status": "error", "message": "Organization ID is required"}, status=400)
    
    organization = get_object_or_404(Organization, id=org_id)

    # security check manual
    profile= get_object_or_404(Profile,user=request.user, organization=organization)
    if not profile:
        return JsonResponse({'error:':'You are not authorized to perform this action'})

    
    members = Profile.objects.filter(organization=organization)
    
    members_data = []
    for member in members:
        members_data.append({
            "user_id": member.user.id,
            "full_name": member.full_name,
            "profile_picture": request.build_absolute_uri(member.profile_picture.url) if member.profile_picture else settings.STATIC_URL + "default-profile.png",
            "email": member.user.email
        })
    
    return JsonResponse({"status": "success", "members": members_data})



# Send task details to members
def send_task_to_members(request):
    """Send task details to selected workspace members via email."""
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)
    
    data = json.loads(request.body)
    org_id = data.get("org_id")
    group_id = data.get("group_id")
    task_id = data.get("task_id")
    selected_members = data.get("selected_members", [])

    if not (org_id and group_id and task_id and selected_members):
        return JsonResponse({"status": "error", "message": "Missing required fields"}, status=400)

    # Fetch organization, group, and task
    organization = get_object_or_404(Organization, id=org_id)
    group = get_object_or_404(Group, id=group_id,organization=organization)
    task = get_object_or_404(Task, id=task_id,group=group,organization=organization)

    # security check manual
    profile= get_object_or_404(Profile,user=request.user, organization=organization)
    if not profile:
        return JsonResponse({'error:':'You are not authorized to perform this action'})

    # Share the Task details
    send_task_details(org_id=organization.id, group_id=group.id, task_id=task.id,selected_members=selected_members)

   
    return JsonResponse({"status": "success", "message": "Task details sent successfully!"})



# TASK RE-ASSIGNMENT
from .utils import *

def reassign_task(request, org_id, group_id, task_id):
    """Reassigns a task to a new user if they belong to the organization & group."""
    if request.method == "POST":
        email = request.POST.get("email")
        new_assignee = get_object_or_404(User, email=email)
        
        # Ensure the user exists in the organization & group
        organization = get_object_or_404(Organization, id=org_id)
        group = get_object_or_404(Group, id=group_id, organization=organization)
        
        # Check if user is in GroupMember model
        if not GroupMember.objects.filter(user=new_assignee, group=group).exists():
            return JsonResponse({"error": "User is not a member of this group!"}, status=400)

        # Update task assignment
        task = get_object_or_404(Task, id=task_id, group=group, organization=organization)
        task.assigned_to = new_assignee
        task.save()

        # send notification about task reassignment
        send_task_assignment_notification(org_id=organization.id, group_id=group.id,task_id=task.id)
        return JsonResponse({"message": "Task reassigned successfully!"})
    
    return JsonResponse({"error": "Invalid request!"}, status=400)


# USER INFO AND SUGGESTIONS TO CONSIDER OR NOT 
def fetch_user_info(request, org_id, group_id):
    """Fetches user info dynamically based on email input."""
    email = request.GET.get("email")
    
    if email:
        user = User.objects.filter(email=email).first()
        if not user:
            return JsonResponse({"error": "User not found!"}, status=404)

        # Ensure user exists in Organization & Group
        organization = get_object_or_404(Organization, id=org_id)
        group = get_object_or_404(Group, id=group_id, organization=organization)

        if not GroupMember.objects.filter(user=user, group=group).exists():
            return JsonResponse({"error": "User is not a member of this group!"}, status=400)

        # Fetch user profile
        profile = Profile.objects.filter(user=user, organization=organization).first()
        # total calpoints earned
        calpoints=CalPoints.objects.filter(organization=organization,user=user).count()

        # Tasks preparation
        # currently having incomplete-tasks 
        tasks=Task.objects.filter(assigned_to=user,organization=organization,group=group,status='pending').count()
        # completed_tasks
        completed_tasks=Task.objects.filter(assigned_to=user, organization=organization, group=group,status='completed').count()


    
        # Prepare the suggestion based on completed task count
        final_message = None

        if completed_tasks == 0:
          final_message = (
          f"{user.username} has not completed any tasks yet. Assigning this task can help them gain experience, "
                   f"but if it's a high-priority task, consider someone more experienced."
       )
        elif completed_tasks == 1:
          final_message = (
           f"{user.username} has completed 1 task. They are starting out and may need guidance, but it’s a good chance for them to contribute."
          )
        elif completed_tasks == 2:
           final_message = (
          f"{user.username} has completed 2 tasks. They are getting familiar with responsibilities. Assign if it's a low-to-medium priority task."
    )
        elif completed_tasks == 3:
          final_message = (
          f"{user.username} has completed 3 tasks. They are building confidence. Assign this task if they are comfortable handling it."
    )
        elif completed_tasks == 4:
           final_message = (
          f"{user.username} has completed 4 tasks. They are becoming a regular contributor. Consider assigning this task if workload permits."
    )
        elif completed_tasks == 5:
          final_message = (
          f"{user.username} has completed 5 tasks. They have a solid start. Assign them if they can manage additional responsibility."
    )
        elif 6 <= completed_tasks <= 20:
           final_message = (
         f"{user.username} has completed {completed_tasks} tasks. They are gaining momentum. Assigning them more tasks can boost efficiency."
    )
        elif 21 <= completed_tasks <= 50:
           final_message = (
          f"{user.username} has completed {completed_tasks} tasks. They are now a consistent performer. They should be prioritized for key assignments."
    )
        elif 51 <= completed_tasks <= 100:
           final_message = (
         f"{user.username} has completed {completed_tasks} tasks! Their experience makes them highly reliable. Assigning them is a great choice."
    )
        elif 101 <= completed_tasks <= 500:
             final_message = (
         f"{user.username} has completed {completed_tasks} tasks! They are one of the top contributors. Prioritize them for high-priority tasks."
      )
        elif 501 <= completed_tasks <= 999:
            final_message = (
         f"{user.username} has completed {completed_tasks} tasks! They are a **power user** and a **high-performance team member**. "
         f"Only assign tasks if they aren’t overloaded."
    )
        elif completed_tasks >= 1000:
              final_message = (
        f"🔥 {user.username} has completed **{completed_tasks}** tasks! This is an **elite level** of contribution. "
        f"They are **indispensable** to the team. Assign **critical** tasks to them only if absolutely necessary!"
     )

        print("FINAL MESSAGE:",final_message)



        
        return JsonResponse({
            "full_name": profile.full_name if profile else user.username,
            "profile_picture": profile.profile_picture.url if profile and profile.profile_picture else None,
            'tasks':tasks,
            'completed_tasks':completed_tasks,
            "calpoints":calpoints,
            "final_message":final_message,
            "message": "User found!"
        })

    return JsonResponse({"error": "Invalid email input!"}, status=400)


# HANDLE TASK AUTOMATIONS

# FETCH ENABLED AUTOMATIONS
@csrf_exempt
def fetch_enabled_automations(request):
    """ Fetch enabled automations for a specific task in an organization & group. """
    if request.method == "GET":
        org_id = request.GET.get("org_id")
        group_id = request.GET.get("group_id")
        task_id = request.GET.get("task_id")

        automation = AutomationTask.objects.filter(
            organization_id=org_id, group_id=group_id, task_id=task_id,user=request.user
        ).first()

        if automation:
            automation_data = {field.name: getattr(automation, field.name) for field in AutomationTask._meta.fields if isinstance(field, models.BooleanField)}
        else:
            automation_data = {}

        return JsonResponse({"status": "success", "automations": automation_data})

    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)



# update the automation
@csrf_exempt
def toggle_automation(request):
    """ Enable or disable a specific automation for a task. """
    if request.method == "POST":
        org_id = request.POST.get("org_id")
        group_id = request.POST.get("group_id")
        task_id = request.POST.get("task_id")
        automation_key = request.POST.get("automation_key")
        status = request.POST.get("status") == "true"

        automation, created = AutomationTask.objects.get_or_create(
            organization_id=org_id, group_id=group_id, task_id=task_id,user=request.user,
            defaults={automation_key: status}
        )

        if not created:
            setattr(automation, automation_key, status)
            automation.save()

        return JsonResponse({"status": "success", "message": f"{automation_key} updated", "enabled": status})

    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)


# DISPLAY SPECTORS
def get_task_details(request, task_id):
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":  # Check if it's an AJAX request
        try:
            task = get_object_or_404(Task, id=task_id)

            # Filter profile to avoid "multiple objects returned" error
            profile = Profile.objects.filter(user=task.created_by).first()  # Get the first profile if multiple exist

            return JsonResponse({
                "success": True,
                "description": task.description,
                "created_by": {
                    "username": task.created_by.username,
                    "email": task.created_by.email,
                },
                "last_login": profile.last_login.isoformat() if profile and profile.last_login else None,
                "profile_picture": profile.profile_picture.url if profile and profile.profile_picture else None  # ✅ FIXED
            })
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    else:
        return JsonResponse({"success": False, "error": "Invalid request"}, status=400)






# ------------------------------------------------------------------------------------------------------------------------------------------------------------
# Add the task to my day 
@login_required
def add_to_my_day(request, org_id , group_id, task_id):
    if request.method == 'POST':

        organization = get_object_or_404(Organization, id=org_id)
        group= get_object_or_404(Group, id=group_id, organization=organization)
        task = get_object_or_404(Task, id=task_id, group=group, organization=organization)

        if not GroupMember.objects.filter(group=group, user=request.user).exists():
            return JsonResponse({'error':'You are not a member of this group!'}, status= 400)
        
        if AddDay.objects.filter(user=request.user, task=task).exists():
            return JsonResponse({'error':'Task is already added to My day'}, status = 400)
        
        add_day_entry= AddDay.objects.create(
            user=request.user,
            organization=organization,
            group=group,
            task=task
        )

        return JsonResponse({
            'message':'Task successfully added to my day',
            'task_id':add_day_entry.id,
            'task_title':task.title
        })
    return JsonResponse({'error':'Invalid request method'}, status = 400)


# Bring the task to perform the actions
@check_org_membership
def my_day_task_detail(request, org_id, group_id, task_id):
    organization = get_object_or_404(Organization, id=org_id)
    group=get_object_or_404(Group, id=group_id, organization=organization)

    task = get_object_or_404(Task, id=task_id, group=group,assigned_to=request.user)
    problems = Problem.objects.filter(task=task,organization=organization,group=group)

    # remained queries
    queries=task.queries_sent


    if not AddDay.objects.filter(task=task, user=request.user).exists():
        raise Http404("This task is not added to My Day for you please add it first!")
    
    task_timer = TaskTimer.objects.filter(task=task, user=request.user).first()
    time_spent = task_timer.accumulated_time if task_timer else timedelta()
    formatted_time = str(time_spent)

    # find earned points if task is completed
    calpoints = None
    if task.status =='completed':
        calpoints = CalPoints.objects.filter(organization=organization,user=request.user).first()
    

    # check if user installed the Extend Tasks app
    # Check if "Extend Tasks" app is installed
    extend_tasks = InstalledMiniApp.objects.filter(organization=organization, user=request.user, mini_app__name="Extend Tasks")

    if extend_tasks.exists():
       print("EXTEND TASKS FOUND::")
    else:
       print("NOT FOUND!")


    print('Time Fetched formatted:', formatted_time)
    return render(request, 'task/my_day_task_detail.html', {
        'organization': organization,
        'group': group,
        'group_id':group_id,
        'org_id':org_id,
        'task': task,
        'formatted_time':formatted_time,
        'problems':problems,
        'extend_tasks':extend_tasks,
        'queries':queries,
        'calpoints':calpoints,
    })


# Handle comments

@csrf_exempt
@login_required
def add_comment(request, org_id, group_id, task_id):
    """
    Handle adding a comment to a task via AJAX.
    Accepts org_id, group_id, task_id from URL and comment data from POST.
    """
    
    organization = get_object_or_404(Organization, id=org_id)
    group = get_object_or_404(Group, id=group_id)

 
    task = get_object_or_404(Task, id=task_id, organization=organization, group=group)


    if not group.members.filter(user=request.user).exists():
        return JsonResponse({'error': 'You are not a member of this group.'}, status=400)


    comment_text = request.POST.get('comment', '').strip()

    if not comment_text:
        return JsonResponse({'error': 'Comment cannot be empty.'}, status=400)


    try:
      comment = TaskComment.objects.create(
         task=task,
         user=request.user,
         organization=organization,
         group=group,
         comment=comment_text,
         created_at=timezone.now()
     )

    # Log the activity
      ActivityLog.objects.create(
        user=request.user,
        organization=organization,
        group=group,
        task=task,
        action='COMMENT',
        details=f"{request.user} Added a comment: '{comment.comment}'"
    )
    except Exception as e:
    
       print(f"Error saving comment or activity log: {e}")


 
    return JsonResponse({
        'message': 'Comment added successfully!',
        'comment': comment.comment,
        'user': comment.user.username,
        'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S')
    }, status=200)


# Handle add note 
@login_required
def add_task_note(request, org_id, group_id, task_id):

    organization = get_object_or_404(Organization, id=org_id)
    group = get_object_or_404(Group, id=group_id, organization=organization)
    task = get_object_or_404(Task, id=task_id, group=group)


    if not group.members.filter(user=request.user).exists():
        raise PermissionDenied("You are not a member of this group and cannot add notes.")

    if request.method == 'POST':
        note_content = request.POST.get('note')

        if note_content:
            note = TaskNote.objects.create(
                task=task,
                user=request.user,
                note=note_content,
                organization=organization,
                group=group,
            )

            # Log the activity
            ActivityLog.objects.create(
              user=request.user,
              organization=organization,
              group=group,
              task=task,
              action='NOTE',
              details=f"{request.user} Added a note: '{note.note}'"
           )
       
            return JsonResponse({
                'note_id': note.id,
                'note': note.note,
                'created_at': note.created_at.strftime('%b %d, %Y, %I:%M %p'),
                'user': note.user.username
            })
        else:
            return JsonResponse({'error': 'Note content cannot be empty'}, status=400)

 
    return JsonResponse({'error': 'Invalid request method'}, status=400)


# Manage task timer
def manage_task_timer(request, org_id, group_id, task_id):
    organization = get_object_or_404(Organization, id=org_id)
    group = get_object_or_404(Group, id=group_id, organization=organization)
    task = get_object_or_404(Task, id=task_id, group=group)

 
    timer, created = TaskTimer.objects.get_or_create(
        user=request.user,
        organization=organization,
        group=group,
        task=task,
        defaults={'start_time': timezone.now(), 'is_running': False, 'accumulated_time': timezone.timedelta()},
    )


    if request.method == "POST":
        if 'start' in request.POST:
            # Start the timer
            if not timer.is_running:
                timer.start_time = timezone.now()
                timer.is_running = True
                timer.save()
                # Log the activity
                ActivityLog.objects.create(
                  user=request.user,
                  organization=organization,
                  group=group,
                  task=task,
                  action='START_TIMER',
                  details=f"{request.user} Started a timer: '{timer.start_time}'"
                )
       
                return JsonResponse({'status': 'started', 'message': 'Timer started successfully.'})

        elif 'stop' in request.POST:
         
            if timer.is_running:
                timer.accumulated_time += timezone.now() - timer.start_time
                timer.is_running = False
                timer.save()
                ActivityLog.objects.create(
                  user=request.user,
                  organization=organization,
                  group=group,
                  task=task,
                  action='STOP_TIMER',
                  details=f" {request.user} Stopeed the timer: '{timer.accumulated_time}'"
                )
       
                return JsonResponse({'status': 'stopped', 'message': 'Timer stopped and time saved successfully.'})

    return JsonResponse({'status': 'error', 'message': 'Invalid action.'})



# Update the task progress 
def update_task_progress(request, org_id, group_id, task_id):
    if request.method == "POST":
        organization = get_object_or_404(Organization, id=org_id)
        group = get_object_or_404(Group, id=group_id, organization=organization)
        task = get_object_or_404(Task, id=task_id, group=group)

        new_progress = int(request.POST.get('progress', 0))

        if 0 <= new_progress <= 100:
            try:
              task.progress = new_progress
              task.progress_update_sent=False
              task.save()
              ActivityLog.objects.create(
                  user=request.user,
                  organization=organization,
                  group=group,
                  task=task,
                  action='PROGRESS_UPDATE',
                  details=f" {request.user} Updated the progreess: '{task.progress}'"
                )
            except Exception as e:
                return JsonResponse({'error':str(e)}, status=400)  
       
            return JsonResponse({'status': 'success', 'progress': task.progress})
        else:
            return JsonResponse({'status': 'error', 'message': 'Progress must be between 0 and 100.'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)



# Fetch activity logs

def fetch_activity_logs(request, org_id, group_id, task_id):
    organization = get_object_or_404(Organization, id=org_id)
    group = get_object_or_404(Group, id=group_id, organization=organization)
    task = get_object_or_404(Task, id=task_id, group=group, organization=organization)

  
    group_member = GroupMember.objects.filter(group=group, user=request.user).exists()
    if not group_member:
        return JsonResponse({'status': 'error', 'message': 'You are not a member of this group.'})


    activity_logs = ActivityLog.objects.filter(
        organization=organization,
        group=group,
        task=task
    ).order_by('-timestamp')  

  
    logs_data = []
    for log in activity_logs:
        logs_data.append({
            'action': log.action,
            'details': log.details,
            'created_at': log.timestamp.strftime('%Y-%m-%d %H:%M:%S'), 
        })

    
    return JsonResponse({'status': 'success', 'activity_logs': logs_data})


# Handle task as completed

@csrf_exempt
def toggle_task_status(request, org_id, group_id,task_id):

    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id, group_id=group_id, organization_id=org_id)

        if not GroupMember.objects.filter(group=task.group, user=request.user).exists():
            return JsonResponse({'status': 'error', 'message': 'Permission denied.'}, status=403)
        

        if task.status != 'completed':
            task.status = 'completed'
            task.save()

            ActivityLog.objects.create(
                user=request.user,
                organization=task.organization,
                group=task.group,
                task=task,
                action = "TASK_COMPLETED",
                details=f" {request.user} Marked the task as completed:'{task.title}'"
            )

      

            activity_logs = ActivityLog.objects.filter(
                user=task.assigned_to,
                task=task,
                organization=task.organization,
                group=task.group
            ).order_by('-timestamp')

            subject = f'Task Completed: {task.title}'
            context = {
                'task':task,
                'organization':task.organization,
                'group':task.group,
                'activity_logs':activity_logs,
                'completed_by':task.assigned_to.username,
                'completed_date':timezone.now(),
            }

            html_message = render_to_string('task/task_completed_email.html', context)

            plain_message= strip_tags(html_message)

          
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [task.created_by.email],
                html_message=html_message,
            )

            return JsonResponse({'status': 'success', 'new_status': 'completed'})
        
        else:
            task.status = 'pending'
            task.save()
            ActivityLog.objects.create(
                user=request.user,
                organization=task.organization,
                group=task.group,
                task=task,
                action = "TASK_PENDING",
                details=f" {request.user} Marked task as pending:'{task.title}'"
            )

            return JsonResponse({'status': 'success', 'new_status': 'pending'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request.'}, status=400)


# Handle task tags 
import json


@csrf_exempt
def update_tags(request, org_id, group_id, task_id):
    if request.method == 'POST':
        try:
           
            data = json.loads(request.body)
            action = data.get('action')
            tag_name = data.get('tag_name')

            organization = get_object_or_404(Organization, id=org_id)
            group = get_object_or_404(Group, id=group_id, organization=organization)
            
            task = get_object_or_404(Task, id=task_id,group=group,organization=organization)
            if not GroupMember.objects.filter(group=group, user=request.user, organization=organization).exists():
               return JsonResponse({'status': 'error', 'message': 'Permission denied.'}, status=403)
        
            if action == 'add' and tag_name in dict(TaskTag.PREDEFINED_TAGS):
                # Check if tag already exists for this task
                existing_tag = TaskTag.objects.filter(task=task, name=tag_name).first()
                if not existing_tag:
                    TaskTag.objects.create(task=task, name=tag_name, organization=organization, group=group)
                    ActivityLog.objects.create(
                        user=request.user,
                        organization=organization,
                        group=group,
                        task=task,
                        action = "TAG_ADDED",
                        details=f" {request.user} Added a tag in task:'{tag_name}'"
                    )
                    return JsonResponse({'tag_name': tag_name}, status=200)
                else:
                    return JsonResponse({'error': 'Tag already added'}, status=400)
            
            elif action == 'remove' and tag_name in dict(TaskTag.PREDEFINED_TAGS):
                # Remove tag from task
                tag = TaskTag.objects.filter(task=task, name=tag_name).first()
                if tag:
                    tag.delete()
                    ActivityLog.objects.create(
                        user=request.user,
                        organization=organization,
                        group=group,
                        task=task,
                        action = "TAG_REMOVED",
                        details=f" {request.user} Removed The tag from task:'{tag_name}'"
                    )
                    return JsonResponse({'tag_name': tag_name}, status=200)
                else:
                    return JsonResponse({'error': 'Tag not found'}, status=400)

            return JsonResponse({'error': 'Invalid action or tag'}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=400)


# Handle time tracking


@login_required 
def save_time(request, org_id, group_id, task_id):
    try:
        
        if request.method != 'POST':
            return JsonResponse({'error': 'Invalid request method'}, status=400)

    
        data = json.loads(request.body)

     
        time_spent = data.get('time_spent')  

        if not time_spent:
            return JsonResponse({'error': 'Time spent is required'}, status=400)

        try:
     
            time_spent = Decimal(time_spent)
        except ValueError:
            return JsonResponse({'error': 'Invalid time format'}, status=400)

    
        organization = get_object_or_404(Organization, id=org_id)
        group = get_object_or_404(Group, id=group_id, organization=organization)
        task = get_object_or_404(Task, id=task_id, group=group)

  
        if not group.members.filter(user=request.user).exists():
            return JsonResponse({'error': 'User is not a member of this group'}, status=400)


        time_tracking_entry, created = TaskTimeTracking.objects.get_or_create(
            task=task,
            user=request.user,
            organization=organization,
            group=group,
            defaults={'time_spent': time_spent}
        )
        ActivityLog.objects.create(
                        user=request.user,
                        organization=organization,
                        group=group,
                        task=task,
                        action = "TIME_SPENT",
                        details=f" {request.user} Spent time on task:'{time_spent}'"
                    )
        print("Time Spent:",time_spent)

        if not created:
        
            time_tracking_entry.time_spent += time_spent
            time_tracking_entry.save()

        
        return JsonResponse({
            'success': True,
            'time_spent': str(time_tracking_entry.time_spent),
            'time_entry_id': time_tracking_entry.id,
            'username': request.user.username
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Raise a problem
@login_required
def create_problem(request, org_id, group_id, task_id):
    if request.method == 'POST':
        try:
         
            data = json.loads(request.body)
            description = data.get('description') 
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format.'}, status=400)

        organization = get_object_or_404(Organization, id=org_id)
        group = get_object_or_404(Group, id=group_id, organization=organization)
        task = get_object_or_404(Task, id=task_id, group=group)

      
        if not group.members.filter(user=request.user).exists():
            return JsonResponse({'error': 'You must be a member of this group to report a problem.'}, status=403)

        if not description:
            return JsonResponse({'error': 'Problem description is required.'}, status=400)

        problem = Problem.objects.create(
            organization=organization,
            group=group,
            task=task,
            reported_by=request.user,
            task_created_by=task.created_by,
            description=description,
        )

        ActivityLog.objects.create(
            user=request.user,
            organization=organization,
            group=group,
            task=task,
            action='RAISED_PROBLEM',
            details=f" {request.user} Raised a problem :'{problem.description}\n reported to {problem.task_created_by}'"

        )

        return JsonResponse({
               'success': 'Problem reported successfully!',
               'problem_id': problem.id,
              'reported_by': problem.reported_by.username,
              'description': problem.description,
              'created_at': problem.created_at.isoformat(),
               'is_resolved': problem.is_resolved,
             }, status=200)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

# resolve the problem

@login_required
def resolve_problem(request, org_id, group_id, task_id, problem_id):
    if request.method == 'POST':
        organization = get_object_or_404(Organization, id=org_id)
        group = get_object_or_404(Group, id=group_id, organization=organization)
        task = get_object_or_404(Task, id=task_id, group=group,organization=organization)
        problem = get_object_or_404(Problem, id=problem_id, task=task, group=group, organization=organization)

        
        print(f"User: {request.user.username}, Task Creator: {task.created_by.username}")
        print(f"User Role in Group: {group.members.filter(user=request.user).first().role if group.members.filter(user=request.user).exists() else 'No Role'}")

       
       
        if not group.members.filter(user=request.user).exists():
            return JsonResponse({'error': 'You do not have permission to resolve this problem.'}, status=403)

       
        problem.is_resolved = True
        ActivityLog.objects.create(
            user=request.user,
            organization=organization,
            group=group,
            task=task,
            action='RESOLVED_PROBLEM',
            details=f" {request.user} Resolved a problem :'{problem.description}\n reported to {problem.task_created_by}'"

        )
        problem.save()

    
        return JsonResponse({
            'success': 'Problem marked as resolved.',
            'problem_id': problem.id,
            'is_resolved': problem.is_resolved,
            'resolved_at': problem.updated_at.isoformat(),
        }, status=200)

   
    return JsonResponse({'error': 'Invalid request method.'}, status=405)



# Handle Note Deletion


@csrf_exempt
def delete_task_note(request, org_id, group_id, task_id, note_id):
    try:
        
        organization = get_object_or_404(Organization, id=org_id)

        
        group = get_object_or_404(Group, id=group_id, organization=organization)

       
        task = get_object_or_404(Task, id=task_id, group=group,organization=organization)

        note = get_object_or_404(TaskNote, id=note_id, task=task, organization=organization, group=group)

   
        if request.user != note.user and not request.user.is_superuser:
            return JsonResponse({'error': 'You are not allowed to delete this note.'}, status=403)
        
        if not group.members.filter(user=request.user).exists():
            return JsonResponse({'error': 'You do not have permission to resolve this problem.'}, status=403)

        note.delete()

        ActivityLog.objects.create(
            user=request.user,
            organization=organization,
            group=group,
            task=task,
            action='NOTE_ELIMINATED',
            details=f" {request.user} Eliminated a note :'{note.note}\n reported to {task.created_by}'"

        )

        return JsonResponse({'message': 'Note deleted successfully!'}, status=200)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

# Edit the note 
@csrf_exempt
def edit_task_note(request, org_id, group_id, task_id, note_id):
   
    organization = get_object_or_404(Organization, id=org_id)


    group = get_object_or_404(Group, id=group_id, organization=organization)

 
    task = get_object_or_404(Task, id=task_id, group=group,organization=organization)

    note = get_object_or_404(TaskNote, id=note_id, task=task, organization=organization, group=group)

    if not group.members.filter(user=request.user).exists():
            return JsonResponse({'error': 'You do not have permission to resolve this problem.'}, status=403)


    if request.method == 'POST':
       
        try:
            data = json.loads(request.body)
            new_note_content = data.get('note')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data provided.'}, status=400)

        if not new_note_content:
            return JsonResponse({'error': 'No note content provided.'}, status=400)

        
        if request.user != note.user and not request.user.is_superuser:
            return JsonResponse({'error': 'You are not allowed to edit this note.'}, status=403)

        note.note = new_note_content
        note.save()
        ActivityLog.objects.create(
            user=request.user,
            organization=organization,
            group=group,
            task=task,
            action='NOTE_AMENDED',
            details=f" {request.user} Amended a note :'{note.note}\n reported to {task.created_by}'"

        )


        return JsonResponse({
            'message': 'Note updated successfully!',
            'note_content': new_note_content,  
            'note_id': note.id,  
        }, status=200)
    
    return JsonResponse({'error': 'Invalid request method.'}, status=405)



# Edit delete comment 

@csrf_exempt
def edit_task_comment(request, org_id, group_id, task_id, comment_id):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            new_comment_content = body.get('comment')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data.'}, status=400)
        
        
        if not new_comment_content:
            return JsonResponse({'error': 'No comment content provided.'}, status=400)

        organization = get_object_or_404(Organization, id=org_id)
        group = get_object_or_404(Group, id=group_id, organization=organization)
        task = get_object_or_404(Task, id=task_id, group=group,organization=organization)
        comment = get_object_or_404(TaskComment, id=comment_id, task=task, organization=organization, group=group)

    
        if request.user != comment.user and not request.user.is_superuser:
            return JsonResponse({'error': 'You are not allowed to edit this comment.'}, status=403)
        
        if not group.members.filter(user=request.user).exists():
            return JsonResponse({'error': 'You do not have permission to resolve this problem.'}, status=403)
        
        comment.comment = new_comment_content
        comment.save()
        ActivityLog.objects.create(
            user=request.user,
            organization=organization,
            group=group,
            task=task,
            action='COMMENT_MODIFIED',
            details=f" The comment {comment.comment} was modified by {request.user}"

        )


        return JsonResponse({
            'message': 'Comment updated successfully!',
            'new_comment': comment.comment
        }, status=200)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)


# Delete comment 

@csrf_exempt
def delete_task_comment(request, org_id, group_id, task_id, comment_id):
    organization = get_object_or_404(Organization, id=org_id)

    group = get_object_or_404(Group, id=group_id, organization=organization)


    task = get_object_or_404(Task, id=task_id, group=group,organization=organization)


    comment = get_object_or_404(TaskComment, id=comment_id, task=task, organization=organization, group=group)


    if request.user != comment.user and not request.user.is_superuser:
        return JsonResponse({'error': 'You are not allowed to delete this comment.'}, status=403)
    
    if not group.members.filter(user=request.user).exists():
            return JsonResponse({'error': 'You do not have permission to resolve this problem.'}, status=403)
        

  
    comment.delete()

    ActivityLog.objects.create(
            user=request.user,
            organization=organization,
            group=group,
            task=task,
            action='COMMENT_DELETED',
            details=f" The comment deletion for - {comment.comment} was performed by {request.user}"

        )

    return JsonResponse({'message': 'Comment deleted successfully!'}, status=200)


# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


# Team leader side features

# Fetch all members to whom manager assigned the tasks
from django.views.generic import ListView
from django.http import HttpResponseForbidden
from django.db import models
from django.core.paginator import Paginator


class AssignedUsersListView(ListView):
    template_name = 'assignment/assigned_users_list.html'
    context_object_name = 'assigned_users'

    def get_queryset(self):
        org_id = self.kwargs['org_id']
        group_id= self.kwargs['group_id']
        team_leader = self.request.user

        organization = get_object_or_404(Organization, id=org_id)

        group = get_object_or_404(Group, id=group_id, organization=organization)

        if group.team_leader != team_leader:
            return HttpResponseForbidden("You are not authorized to perform this action! please contact to your workspace admin")
        
        return (
            Task.objects.filter(group=group, created_by=team_leader)
            .exclude(assigned_to=team_leader)
            .values(
                'assigned_to__id',
                'assigned_to__username',
                'assigned_to__email',
                'assigned_to__profiles__profile_picture',
            )
            .annotate(
                task_count=models.Count('id'),
                pending_count=models.Count('id', filter=models.Q(status='pending')),
                completed_count=models.Count('id', filter=models.Q(status='completed')),
                in_progress_count=models.Count('id', filter=models.Q(status='in_progress')),
                nearest_deadline=models.Min('deadline'),
            )
        )
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
      
        org_id = self.kwargs['org_id']
        group_id = self.kwargs['group_id']
        user_id =self.request.user.id

        context['org_id'] = org_id
        context['group_id'] = group_id
        context['user_id'] = user_id

        return context



# Fetch all tasks team leader assignhed to the user]

# Fetch all tasks team leader assigned to the user
def user_tasks_view(request, org_id, group_id, user_id):
    organization = get_object_or_404(Organization, id=org_id)
    group = get_object_or_404(Group, id=group_id, organization=organization)

    if group.team_leader != request.user:
        return HttpResponseForbidden("You are not authorized to view this information.")

    user = get_object_or_404(User, id=user_id)

    if group.team_leader != request.user:
        return HttpResponseForbidden("You are not authorized to perform this action! Please contact your workspace admin.")


    tasks = Task.objects.filter(group=group, created_by=request.user, assigned_to=user, organization=organization)
    
    
    tasks_in_add_day = AddDay.objects.filter(user=user, task__in=tasks)
    print("ADD DAY TASKS:", tasks_in_add_day)

 
    tasks_added = tasks_in_add_day

    tasks_without_add_day = tasks.exclude(id__in=tasks_in_add_day.values_list('task', flat=True))


    tasks_completed = tasks.filter(status='completed')


    tasks_added = tasks_added.order_by('-task__updated_at')
    tasks_without_add_day = tasks_without_add_day.order_by('-deadline')
    tasks_completed = tasks_completed.order_by('-updated_at')

   
    return render(request, 'assignment/user_tasks.html', {
        'user': user,
        'organization': organization,
        'group': group,
        'tasks_added': tasks_added, 
        'tasks_without_add_day': tasks_without_add_day,  
        'tasks_completed': tasks_completed,  
    })



# Detailed tasks details 

class TaskDetailView(View):
    def get(self, request, org_id, group_id, task_id, user_id):

        organization = get_object_or_404(Organization, id=org_id)
        group=get_object_or_404(Group, id=group_id, organization=organization)
       
        task = get_object_or_404(Task, id=task_id, organization=organization, group=group)
        
 
        user = get_object_or_404(User, id=user_id)
        if task.created_by != user and not task.group.members.filter(user=user).exists():
            raise Http404("You don't have permission to view this task.")
        
        profile_pic = get_object_or_404(Profile, user=request.user, organization=organization).profile_picture

        comments = TaskComment.objects.filter(task=task).order_by('-created_at')
        notes = TaskNote.objects.filter(task=task).order_by('-created_at')
        time_tracking = TaskTimeTracking.objects.filter(task=task, user=user)
        activity_logs = ActivityLog.objects.filter(task=task).order_by('-timestamp')
        problems = Problem.objects.filter(task=task)
        tags = TaskTag.objects.filter(task=task)

        context = {
            'organization':organization,
            'group':group,
            'task': task,
            'comments': comments,
            'notes': notes,
            'time_tracking': time_tracking,
            'activity_logs': activity_logs,
            'problems': problems,
            'tags': tags,
            'user': user,
            'profile_pic':profile_pic,
        }

        return render(request, 'assignment/task_detail.html', context)


# Team leader can comment on the task
@login_required
@csrf_exempt
def add_task_comment(request, org_id, group_id, task_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            
            organization = get_object_or_404(Organization, id=org_id)
            group = get_object_or_404(Group, id=group_id, organization=organization)
            task = get_object_or_404(Task, id=task_id, group=group)

        
            if group.team_leader != request.user:
                return JsonResponse({'error': 'You are not authorized to comment on this task.'}, status=403)

            comment_text = data.get('comment')
            if not comment_text:
                return JsonResponse({'error': 'Comment text is required.'}, status=400)

         
            comment = TaskComment.objects.create(
                task=task,
                user=request.user,
                organization=organization,
                group=group,
                comment=comment_text
            )

            ActivityLog.objects.create(
              user=request.user,
              organization=organization,
              group=group,
              task=task,
              action='COMMENT',
              details=f" {request.user} - Team Leader Commented {comment_text}"

         )

          
            return JsonResponse({
                'message': 'Comment added successfully!',
                'comment': {
                    'id': comment.id,
                    'user': comment.user.username,
                    'text': comment.comment,
                    'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }
            })

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data.'}, status=400)

 
    return JsonResponse({'error': 'Invalid request method.'}, status=405)



# FETCH RECENT TABS!

@login_required
def fetch_recent_tabs(request):
    """ Fetch all recent tabs for the authenticated user """
    recent_tabs = RecentVisit.objects.filter(user=request.user).order_by('-visited_at')[:20]

    # Serialize data
    data = [
        {
            "id": tab.id,
            "url": tab.url,
            "visited_at": tab.visited_at.strftime("%Y-%m-%d %H:%M:%S"),
            "screenshot": tab.screenshot.url if tab.screenshot else None
        }
        for tab in recent_tabs
    ]
    
    return JsonResponse({"status": "success", "recent_tabs": data})

# clear recent tabs
@csrf_exempt  
@login_required
def clear_recent_tabs(request):
    """ Clear all recent tabs for the authenticated user """
    if request.method == "POST":
        RecentVisit.objects.filter(user=request.user).delete()
        return JsonResponse({"status": "success", "message": "Recent tabs cleared!"})
    
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)




