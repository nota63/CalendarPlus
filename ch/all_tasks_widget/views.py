from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from group_tasks.models import Task,TaskTag
from accounts.models import Organization, Profile
from django.db.models import Count
from django.db.models.functions import TruncDate
from datetime import timedelta
from django.utils import timezone

# Widget 1) Number of tasks in progress 

@csrf_exempt
@login_required
def tasks_in_progress_count(request, org_id):
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    # check access
    if not Profile.objects.filter(user=request.user, organization_id=org_id).exists():
        return JsonResponse({'error:':'Unauthorized access'}, status=400)
    

    try:
        user = request.user
        task_count = Task.objects.filter(
            organization_id=org_id,
            assigned_to=user,
            status='in_progress'
        ).count()

        return JsonResponse({'count': task_count})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# // Widget 2 Completed Tasks Per Group------------------------------------------------------------------------------------------------------------------

@login_required
def completed_tasks_summary(request, org_id):
    user = request.user

    # Filter completed tasks assigned to the user in the given organization
    completed_tasks = Task.objects.filter(
        organization_id=org_id,
        assigned_to=user,
        status='completed'
    )

    # Total completed tasks
    total_completed = completed_tasks.count()

    # Group-wise breakdown
    groupwise = (
        completed_tasks
        .values('group__name')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    return JsonResponse({
        "total_completed": total_completed,
        "groupwise": list(groupwise)
    })


# // widget 3 tasks status over time -----------------------------------------------------------------------------------------------------------
  
def status_over_time_view(request, org_id):
    user = request.user
    today = timezone.now().date()
    days = 7
    start_date = today - timedelta(days=days - 1)
    date_range = [start_date + timedelta(days=i) for i in range(days)]

    # Get all statuses for consistency
    all_statuses = [choice[0] for choice in Task._meta.get_field('status').choices]

    # Query & group data
    task_data = (
        Task.objects.filter(
            organization_id=org_id,
            assigned_to=user,
            deadline__date__range=(start_date, today)
        )
        .annotate(day=TruncDate('deadline'))
        .values('day', 'status')
        .annotate(count=Count('id'))
        .order_by('day')
    )

    # Format like: { date: { status: count } }
    stats_map = {}
    for entry in task_data:
        date_str = entry['day'].strftime('%Y-%m-%d')
        status = entry['status']
        count = entry['count']
        stats_map.setdefault(date_str, {})
        stats_map[date_str][status] = count

    # Final response with 0-fill
    final_data = {
        'labels': [d.strftime('%Y-%m-%d') for d in date_range],
        'datasets': []
    }

    # Create dataset per status
    for status in all_statuses:
        dataset = {
            'label': status.replace('_', ' ').title(),
            'data': [],
        }
        for date in date_range:
            date_str = date.strftime('%Y-%m-%d')
            dataset['data'].append(stats_map.get(date_str, {}).get(status, 0))
        final_data['datasets'].append(dataset)

    return JsonResponse({'data': final_data})



# // Widget 4) Tag usage bar chart-------------------------------------------------------------------------------------------------------------  
def tag_usage_summary(request, org_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    tags_data = (
        TaskTag.objects.filter(organization_id=org_id)
        .values('name')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    response_data = {
        'labels': [entry['name'] for entry in tags_data],
        'data': [entry['count'] for entry in tags_data],
    }

    return JsonResponse(response_data)





