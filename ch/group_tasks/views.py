from django.shortcuts import render, redirect , get_list_or_404
from .models import Task, TaskNote, TaskComment , TaskTag, ActivityLog
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
from .models import AddDay



@login_required
def task_calendar(request, org_id, group_id):
    # Fetch the group and organization based on IDs
    group = get_object_or_404(Group, id=group_id, organization_id=org_id)
    organization = get_object_or_404(Organization, id=org_id)

    # Ensure that the user is assigned to this group
    if not GroupMember.objects.filter(group=group, user=request.user).exists():
        raise Http404("You are not a member of this group.")


    tasks = Task.objects.filter(group=group, assigned_to=request.user).order_by('-created_at')

    # Pagination
    paginator = Paginator(tasks, 2) 
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

    return render(request, 'task/task_calendar.html', {
        'tasks': task_data,
        'group': group,
        'organization': organization,
        'page_obj': page_obj,  
    })





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

def my_day_task_detail(request, org_id, group_id, task_id):
    organization = get_object_or_404(Organization, id=org_id)
    group=get_object_or_404(Group, id=group_id, organization=organization)

    task = get_object_or_404(Task, id=task_id, group=group)

    if not AddDay.objects.filter(task=task, user=request.user).exists():
        raise Http404("This task is not added to My Day for you please add it first!")
    
    # Fetch the time 
    # Fetch the task timer directly for the current user and task
   # Inside your view
    task_timer = TaskTimer.objects.filter(task=task, user=request.user).first()
    time_spent = task_timer.accumulated_time if task_timer else timedelta()
    formatted_time = str(time_spent)

    print('Time Fetched formatted:', formatted_time)
    return render(request, 'task/my_day_task_detail.html', {
        'organization': organization,
        'group': group,
        'group_id':group_id,
        'org_id':org_id,
        'task': task,
        'formatted_time':formatted_time,
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
        details=f"Added a comment: '{comment.comment}'"
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
              details=f"Added a note: '{note.note}'"
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
                  details=f"Started a timer: '{timer.start_time}'"
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
                  details=f"Stopeed the timer: '{timer.accumulated_time}'"
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
                  details=f"Updated the progreess: '{task.progress}'"
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
        user=request.user,
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