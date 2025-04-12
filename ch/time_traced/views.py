from group_tasks.models import Task, TaskTimeTracking
from accounts.models import Organization , Profile
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q

# 1)Fetch time traced
def task_time_tracking_summary(request, org_id):
    user = request.user

    # check access
    if not Profile.objects.filter(user=user,organization_id=org_id).exists():
        return JsonResponse({'error:':'You are not authorized to view this!'}, status=400)

    # Fetch only tracked tasks assigned to the user
    time_logs = TaskTimeTracking.objects.filter(
        organization_id=org_id,
        task__assigned_to=user
    ).select_related('task')

    response_data = []
    for log in time_logs:
        response_data.append({
            'task_title': log.task.title,
            'start_time': log.start_time.strftime('%Y-%m-%d %H:%M'),
            'end_time': log.end_time.strftime('%Y-%m-%d %H:%M') if log.end_time else 'In Progress',
            'time_spent': float(log.time_spent),
            'duration': round(log.get_duration(), 2)  # In hours
        })

    return JsonResponse({'success': True, 'data': response_data})


# Widget 2) High priority tasks widget ---------------------------------------------------------------------------------------------------------------

@login_required
def high_priority_tasks_widget(request, org_id):
    tasks = Task.objects.filter(
        organization_id=org_id,
        assigned_to=request.user,
        priority__in=['high', 'urgent'],
        status__in=['pending', 'in_progress', 'overdue', 'pending_approval', 'need_changes']
    ).select_related('group')

    task_data = [
        {
            "id": task.id,
            "title": task.title,
            "group_name": task.group.name,
            'progress':task.progress,
            "status": task.status.replace("_", " ").title(),
            "deadline": task.deadline.strftime('%Y-%m-%d %H:%M')
        }
        for task in tasks
    ]

    return JsonResponse({"tasks": task_data})

