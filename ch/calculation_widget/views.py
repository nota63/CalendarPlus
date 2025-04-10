from django.shortcuts import render
from groups.models import Group
from accounts.models import Profile, Organization, MeetingOrganization, EventOrganization, BookingOrganization
from group_tasks.models import Task
from django.db.models import Q,Avg
from django.http import JsonResponse
from django.db.models import Count, Q, Avg
from django.utils.timezone import now, timedelta

# Create your views here.


# get sum calculation
def get_sum_calculation(request, org_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    user = request.user

    # Fetch all at once if possible
    total_tasks = Task.objects.filter(assigned_to=user, organization_id=org_id).count()
    total_meetings = MeetingOrganization.objects.filter(
        Q(user=user) | Q(invitee=user) | Q(participants=user),
        organization_id=org_id  # Fixed typo from orgnization_id
    ).distinct().count()  # Distinct to avoid duplicate count if multiple relations
    total_events = EventOrganization.objects.filter(user=user, organization_id=org_id).count()
    total_bookings = BookingOrganization.objects.filter(organization_id=org_id, invitee=user).count()

    return JsonResponse({
        'total_tasks': total_tasks,
        'total_meetings': total_meetings,
        'total_events': total_events,
        'total_bookings': total_bookings,
    })


# Tasks count analytics
def get_task_analytics(request, org_id):
    user = request.user
    today = now().date()
    end_of_week = today + timedelta(days=7)

    tasks = Task.objects.filter(organization_id=org_id, assigned_to=user)

    total_tasks = tasks.count()
    completed_tasks = tasks.filter(status='completed').count()
    pending_tasks = tasks.filter(status='pending').count()
    in_progress_tasks = tasks.filter(status='in_progress').count()
    overdue_tasks = tasks.filter(status='overdue').count()

    completion_rate = round((completed_tasks / total_tasks) * 100, 2) if total_tasks else 0

    tasks_due_today = tasks.filter(deadline__date=today).count()
    tasks_due_this_week = tasks.filter(deadline__date__range=[today, end_of_week]).count()

    urgent_tasks = tasks.filter(priority='urgent').count()
    average_progress = tasks.aggregate(avg=Avg('progress'))['avg'] or 0

    return JsonResponse({
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
        'overdue_tasks': overdue_tasks,
        'completion_rate': completion_rate,
        'tasks_due_today': tasks_due_today,
        'tasks_due_this_week': tasks_due_this_week,
        'urgent_tasks': urgent_tasks,
        'average_progress': round(average_progress, 2),
    })
