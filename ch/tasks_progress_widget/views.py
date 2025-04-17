from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.utils.timezone import now
from django.db.models import Count, Q
from groups.models import Group
from accounts.models import Organization, Profile
from group_tasks.models import Task
from django.contrib.auth.models import User


def group_task_analytics_view(request, org_id):
    organization = get_object_or_404(Organization, id=org_id)
    groups = Group.objects.filter(organization=organization).prefetch_related('tasks')

    all_data = []

    for group in groups:
        tasks = group.tasks.all()
        total_tasks = tasks.count()

        # Status counts
        status_count = tasks.values('status').annotate(count=Count('id'))
        status_map = {item['status']: item['count'] for item in status_count}

        # Base counts
        completed_tasks = status_map.get('completed', 0)
        in_progress_tasks = status_map.get('in_progress', 0)
        pending_tasks = status_map.get('pending', 0)
        cancelled_tasks = status_map.get('cancelled', 0)
        need_changes = status_map.get('need_changes', 0)
        pending_approval = status_map.get('pending_approval', 0)
        overdue_tasks = tasks.filter(deadline__lt=now()).exclude(status='completed').count()
        urgent_tasks = tasks.filter(priority='urgent').count()

        progress_percent = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0

        # Deadline insights
        upcoming = tasks.filter(deadline__gte=now()).order_by('deadline').first()
        latest = tasks.order_by('-deadline').first()

        # Active members (assigned to at least one task)
        active_members = tasks.values('assigned_to').distinct().count()

        # Top performers by completed tasks
        top_users = (
            tasks.filter(status='completed')
            .values('assigned_to__id', 'assigned_to__username')
            .annotate(completed=Count('id'))
            .order_by('-completed')[:3]
        )

        top_contributors = [
            {'user_id': user['assigned_to__id'], 'username': user['assigned_to__username'], 'completed_tasks': user['completed']}
            for user in top_users
        ]

        group_data = {
            'group_id': group.id,
            'group_name': group.name,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'in_progress_tasks': in_progress_tasks,
            'pending_tasks': pending_tasks,
            'cancelled_tasks': cancelled_tasks,
            'need_changes': need_changes,
            'pending_approval': pending_approval,
            'progress_percent': progress_percent,
            'overdue_tasks_count': overdue_tasks,
            'urgent_tasks_count': urgent_tasks,
            'next_deadline': upcoming.deadline if upcoming else None,
            'latest_deadline': latest.deadline if latest else None,
            'active_members_count': active_members,
            'top_contributors': top_contributors,
        }

        all_data.append(group_data)

    return JsonResponse({
        'organization': {
            'id': organization.id,
            'name': organization.name,
        },
        'group_analytics': all_data
    }, safe=False)
