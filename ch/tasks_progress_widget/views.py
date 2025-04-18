from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.utils.timezone import now
from django.db.models import Count, Q
from groups.models import Group,GroupMember
from accounts.models import Organization, Profile
from group_tasks.models import Task
from django.contrib.auth.models import User
from django.db.models.functions import TruncDay,TruncDate
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST,require_GET
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import csrf_exempt

# 1) Fetch groups 
def group_leader_info_view(request, org_id):
    # Fetch the organization object
    organization = get_object_or_404(Organization, id=org_id)
    
    # Fetch all groups under the specified organization
    groups = Group.objects.filter(organization=organization)

    group_leader_data = []

    for group in groups:
        # Get the team leader from the Profile model (assuming 'team_leader' is a ForeignKey to Profile)
        team_leader_profile =Profile.objects.filter(organization_id=org_id,user=group.team_leader).first()  # assuming 'team_leader' is a ForeignKey to User
        # check access 
        try:
            profile = Profile.objects.get(user=request.user, organization_id=org_id)
        except Profile.DoesNotExist:
            return JsonResponse({'error': 'Access denied'}, status=403)

        # Check permission
        if not profile.is_admin and request.user != group.team_leader:
            return JsonResponse({'error': 'Access denied'}, status=403)

                
        # Append group data along with team leader's profile picture
        group_leader_data.append({
            'id':group.id,
            'group_name': group.name,
            'team_leader': {
                'username': team_leader_profile.user.username,  # Assuming user is the related User instance
                'profile_picture': team_leader_profile.profile_picture.url if team_leader_profile.profile_picture else None
            }
        })

    return JsonResponse({
        'organization': {
            'id': organization.id,
            'name': organization.name,
        },
        'groups': group_leader_data
    }, safe=False)




# 2) group analytics
def group_task_analytics_view(request, org_id, group_id):
    # Fetch the organization object
    organization = get_object_or_404(Organization, id=org_id)
    
    # Fetch the specific group for the given group_id within the organization
    group = get_object_or_404(Group, id=group_id, organization=organization)
    # check access 
    try:
        profile = Profile.objects.get(user=request.user, organization_id=org_id)
    except Profile.DoesNotExist:
        return JsonResponse({'error': 'Access denied'}, status=403)

    # Check permission
    if not profile.is_admin and request.user != group.team_leader:
        return JsonResponse({'error': 'Access denied'}, status=403)

    
    # Fetch all tasks for the specific group
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

    # Organize group analytics data
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

    return JsonResponse({
        'organization': {
            'id': organization.id,
            'name': organization.name,
        },
        'group_analytics': group_data
    }, safe=False)

# Widget 2) Group Task completion velocity-----------------------------------------------------------------------------------------------------

def group_task_completion_velocity(request, org_id):
    try:
        org = Organization.objects.get(id=org_id)
    except Organization.DoesNotExist:
        return JsonResponse({'error': 'Invalid organization.'}, status=404)

    # Optional query params
    try:
        days = int(request.GET.get('days', 14))
        days = min(max(days, 1), 90)  # restrict between 1 and 90 days
    except ValueError:
        days = 14

    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)

    groups = Group.objects.filter(organization=org)
    response_data = []

    for group in groups:
        task_qs = (
            Task.objects.filter(
                organization=org,
                group=group,
                status='completed',
                deadline__date__range=(start_date, end_date),
                deadline__isnull=False
            )
            .annotate(day=TruncDay('deadline'))
            .values('day')
            .annotate(total=Count('id'))
            .order_by('day')
        )

        group_data = {
            'group_name': group.name,
            'data': [
                {
                    'x': item['day'].isoformat(),
                    'y': item['total']
                }
                for item in task_qs
            ]
        }

        # Even if no tasks, return group with empty data
        response_data.append(group_data)

    return JsonResponse({'series': response_data}, status=200)

# // Widget 3) Assign Task ---------------------------------------------------------------------------
@login_required
def get_assignable_groups_ajax(request, org_id):
    try:
        profile = Profile.objects.get(user=request.user, organization_id=org_id)
    except Profile.DoesNotExist:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    

    groups = Group.objects.filter(organization_id=org_id).values('id', 'name')

    return JsonResponse({'groups': list(groups)}, status=200)


# Assign the task
@csrf_exempt
@require_POST
def assign_task_to_group_member(request, org_id, group_id):
    try:
        data = request.POST

        # Get and validate organization and group
        try:
            organization = Organization.objects.get(id=org_id)
            group = Group.objects.get(id=group_id, organization=organization)
        except Organization.DoesNotExist:
            return JsonResponse({'error': 'Organization not found.'}, status=404)
        except Group.DoesNotExist:
            return JsonResponse({'error': 'Group not found in this organization.'}, status=404)

        # Resolve user from GroupMember by email and validate org and group membership
        email = data.get('assigned_email')
        if not email:
            return JsonResponse({'error': 'Email is required to assign task.'}, status=400)

        try:
            group_member = GroupMember.objects.select_related('user').get(
                group=group,
                organization=organization,
                user__email=email
            )
            assigned_user = group_member.user
        except GroupMember.DoesNotExist:
            return JsonResponse({'error': 'User with this email is not a member of this group in this organization.'}, status=400)

        # Create task
        task = Task.objects.create(
            organization=organization,
            group=group,
            created_by=request.user,
            assigned_to=assigned_user,

            title=data.get('title'),
            description=data.get('description'),
            project_plan=data.get('project_plan', ''),
            priority=data.get('priority', 'medium'),
            status=data.get('status', 'pending'),

            deadline=parse_datetime(data.get('deadline')),
            start_date=parse_datetime(data.get('start_date')),
            end_date=parse_datetime(data.get('end_date')),
        )

        return JsonResponse({
            'success': True,
            'message': f'Task \"{task.title}\" assigned to {assigned_user.email}.',
            'task_id': task.id
        })

    except Exception as e:
        return JsonResponse({'error': f'Something went wrong: {str(e)}'}, status=500)


# Get User by email (live preview)
@require_GET
def get_user_by_email(request, org_id, group_id):
    email = request.GET.get("email")
    if not email:
        return JsonResponse({"error": "Email is required."}, status=400)

    try:
        group = get_object_or_404(Group, id=group_id, organization_id=org_id)
        group_member = GroupMember.objects.select_related('user').get(
            group=group,
            organization_id=org_id,
            user__email=email
        )
        user = group_member.user
        data = {
            "full_name": user.get_full_name() or user.username,
            "email": user.email,
            "avatar_url": getattr(user.profile, "profile_picture", None) or "/static/default-avatar.png"
        }
        return JsonResponse({"success": True, "user": data})

    except GroupMember.DoesNotExist:
        return JsonResponse({"error": "User not found in this group."}, status=404)