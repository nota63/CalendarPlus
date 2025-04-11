from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from group_tasks.models import Task, SubTask
from django.shortcuts import redirect, get_object_or_404
from accounts.models import Organization, Profile
from django.utils.timezone import now
from datetime import timedelta


# Fetch tasks progress along with group names
@login_required
def user_task_progress_widget(request, org_id):
    user = request.user

    # check access
    if not Profile.objects.filter(user_id=user.id, organization_id=org_id).exists():
        return JsonResponse({'error': 'Access denied'}, status=403)

    tasks = Task.objects.filter(
        organization_id=org_id,
        assigned_to=user
    ).select_related("group").values(
        'id',
        "title",
        "progress",
        "group__name"
    )

    return JsonResponse({
        "tasks": list(tasks)
    }, safe=False)


# get task progress detail
@login_required
def get_task_progress_details(request, org_id, task_id):
    org = get_object_or_404(Organization, id=org_id)
    task = get_object_or_404(Task, id=task_id, organization=org)

    if not Profile.objects.filter(user_id=request.user.id, organization_id=org_id).exists():
      return JsonResponse({'error': 'Access denied'}, status=403)


    created_by = task.created_by.get_full_name() or task.created_by.username
    deadline = task.deadline
    remaining_days = (deadline.date() - now().date()).days

    subtasks = SubTask.objects.filter(task=task, organization=org)
    completed = subtasks.filter(status='completed').count()
    total = subtasks.count()

    return JsonResponse({
        "assigned_by": created_by,
        "deadline": deadline.strftime("%Y-%m-%d"),
        "remaining_days": remaining_days,
        "subtasks": {
            "completed": completed,
            "total": total,
        }
    })



# Widget 2 ) Overdue Tasks
@login_required
def get_overdue_tasks(request, org_id):
    user = request.user

    # Check if user is part of the org
    if not Profile.objects.filter(user=user, organization_id=org_id).exists():
        return JsonResponse({'error': 'Access denied.'}, status=403)

    # Fetch tasks assigned to user, past deadline, and not completed/cancelled
    overdue_tasks = Task.objects.select_related('group').filter(
        assigned_to=user,
        organization_id=org_id,
        deadline__lt=now(),
        status__in=['pending', 'in_progress', 'pending_approval', 'need_changes']
    ).values(
        'id', 'title', 'deadline', 'group__name','group__id','status'
    ).order_by('deadline')

    return JsonResponse({'overdue_tasks': list(overdue_tasks)})


# Widget 3) Tasks Due Soon in 14 days -----------------------------------------------------------------------------------------------
@login_required
def get_due_soon_tasks(request, org_id):
    user = request.user

    # Check access via Profile
    if not Profile.objects.filter(user=user, organization_id=org_id).exists():
        return JsonResponse({'error': 'Access denied.'}, status=403)

    # Fetch tasks due in next 14 days, not completed or cancelled
    today = now().date()
    two_weeks_later = today + timedelta(days=14)

    due_soon_tasks = Task.objects.select_related('group').filter(
        organization_id=org_id,
        assigned_to=user,
        deadline__date__gte=today,
        deadline__date__lte=two_weeks_later,
        status__in=['pending', 'in_progress', 'overdue', 'pending_approval', 'need_changes']
    ).values(
        'id', 'title', 'deadline', 'group__name', 'group_id'
    ).order_by('deadline')

    return JsonResponse({'due_soon_tasks': list(due_soon_tasks)})