from django.shortcuts import render, redirect , get_list_or_404
from .models import (Task, TaskNote, TaskComment , TaskTag, ActivityLog,RecentVisit,MeetingTaskQuery,CommunicateTask)
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

# Fetch all members to whom he assigned the tasks
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
