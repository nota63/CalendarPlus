from group_tasks.models import Task, TaskTimeTracking,CalPoints
from accounts.models import Organization , Profile
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q,Sum

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


# //  Widget 3) Total Calpoints Earned --------------------------------------------------------------------------------------------------------

@login_required
def get_calpoints_balance_view(request, org_id):
    user = request.user
    try:
        profile = Profile.objects.get(user=user, organization_id=org_id)
    except Profile.DoesNotExist:
        return JsonResponse({'error': 'Profile not found for this organization.'}, status=404)

    calpoints = CalPoints.objects.filter(user=user, organization_id=org_id)
    total_points = calpoints.aggregate(total=Sum('points'))['total'] or 0

    return JsonResponse({
        'total_points': total_points,
        'username': profile.full_name or user.username,
        'profile_pic': profile.profile_picture.url if profile.profile_picture else '',
        'organization_name': profile.organization.name
    })
