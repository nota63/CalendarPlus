from django.shortcuts import render, redirect, get_object_or_404
from conversation.models import Conversation, Message
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.db.models import Q,Sum,Count
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from accounts.models import Profile, Organization
from group_tasks.models import TaskTimeTracking,Task
from django.views.decorators.http import require_GET
# Create your views here.
# fetch users within the workspace

@login_required
def fetch_chat_users(request, org_id):
    profiles = Profile.objects.filter(organization_id=org_id).exclude(user=request.user)
    
    data = []
    for profile in profiles:
        data.append({
            'user_id': profile.user.id,
            'full_name': profile.full_name,
            'profile_picture': profile.profile_picture.url if profile.profile_picture else None
        })

    return JsonResponse({'users': data})

# Get Or Create the conversation
@csrf_exempt
@login_required
def handle_chat(request):
    if request.method == "POST":
        receiver_id = request.POST.get("receiver_id")
        text = request.POST.get("text", "").strip()
        org_id = request.POST.get("org_id")
        code_snippet = request.POST.get("code_snippet", "").strip()
        uploaded_file = request.FILES.get("file")

        if not receiver_id or not (text or code_snippet or uploaded_file):
            return JsonResponse({'error': 'Missing message content'}, status=400)

        receiver = User.objects.get(id=receiver_id)
        user1, user2 = sorted([request.user, receiver], key=lambda u: u.id)

        # Get or create conversation
        conversation, created = Conversation.objects.get_or_create(
            user1=user1,
            user2=user2,
            organization_id=org_id
        )

        # Save the message
        message = Message.objects.create(
            organization_id=org_id,
            conversation=conversation,
            sender=request.user,
            text=text if text else None,
            code_snippet=code_snippet if code_snippet else None,
            file=uploaded_file if uploaded_file else None
        )

        return JsonResponse({
            'status': 'Message sent',
            'message_id': message.id,
            'timestamp': message.timestamp.strftime("%Y-%m-%d %H:%M"),
            'sender': request.user.id,
            'text': message.text,
            'file_url': message.file.url if message.file else None,
            'code_snippet': message.code_snippet
        })

    elif request.method == "GET":
        receiver_id = request.GET.get("receiver_id")
        org_id = request.GET.get("org_id")

        if not receiver_id:
            return JsonResponse({'error': 'Receiver ID missing'}, status=400)

        receiver = User.objects.get(id=receiver_id)
        user1, user2 = sorted([request.user, receiver], key=lambda u: u.id)

        try:
            conversation = Conversation.objects.get(
                user1=user1,
                user2=user2,
                organization_id=org_id
            )
        except Conversation.DoesNotExist:
            return JsonResponse({'messages': []})

        messages = conversation.messages.order_by("timestamp")
        messages_data = [
            {
                "id": msg.id,
                "sender": msg.sender.id,
                "text": msg.text,
                "file_url": msg.file.url if msg.file else None,
                "code_snippet": msg.code_snippet,
                "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M"),
                "is_read": msg.is_read
            }
            for msg in messages
        ]

        return JsonResponse({"messages": messages_data})


# Widget 2)Total time traced----------------------------------------------------------------------------------------------------------------

@login_required
def time_spent_battery_chart(request, org_id):
    try:
        organization = Organization.objects.get(id=org_id)

        # Sum of time_spent per user (if needed you can just remove `.values('user__username')` to get global)
        time_data = (
            TaskTimeTracking.objects
            .filter(organization=organization,user=request.user)
            .values('user__username')
            .annotate(total_time=Sum('time_spent'))
            .order_by('-total_time')
        )

        chart_data = []
        for item in time_data:
            username = item['user__username']
            time_hours = float(item['total_time'])
            # For example, treat 8 hrs = full battery
            battery_level = min(100, round((time_hours / 8) * 100))

            chart_data.append({
                'user': username,
                'time_hours': time_hours,
                'battery_level': battery_level,
            })

        return JsonResponse({'status': 'success', 'data': chart_data})
    
    except Organization.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Organization not found'}, status=404)

# Time spent by group
def time_spent_by_group_view(request, org_id):
    time_data = (
        TaskTimeTracking.objects.filter(organization_id=org_id,user=request.user)
        .values("group__name")
        .annotate(total_hours=Sum("time_spent"))
        .order_by("-total_hours")
    )

    result = [
        {
            "group": entry["group__name"],
            "time_hours": float(entry["total_hours"]) if entry["total_hours"] else 0
        }
        for entry in time_data
    ]

    return JsonResponse({
        "status": "success",
        "data": result
    })

# Widget 4) Total tasks by assignee-------------------------------------------------------------------------------------------------------------------------------------------
@login_required
def fetch_user_pending_tasks_by_org(request, org_id):
    user = request.user
    try:
        organization = Organization.objects.get(id=org_id)
    except Organization.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Organization not found."}, status=404)

    # Active task statuses except 'completed'
    active_statuses = [
        'pending', 'in_progress', 'overdue', 'pending_approval', 'need_changes'
    ]

    tasks_qs = Task.objects.filter(
        assigned_to=user,
        organization=organization,
        status__in=active_statuses
    ).select_related('group')

    task_data = [
        {
            'id': task.id,
            'title': task.title,
            'status': task.status,
            'priority': task.priority,
            'deadline': task.deadline,
            'group_name': task.group.name if task.group else "No Group"
        }
        for task in tasks_qs
    ]

    return JsonResponse({
        "status": "success",
        "total_tasks": tasks_qs.count(),
        "data": task_data
    })



# // Widget 5) Unassigned tasks ------------------------------------------------------------------------------------------------------------------------------------------------


@login_required
@require_GET
def task_assignment_summary(request, org_id):
    user = request.user

    # Get total tasks in this organization
    total_tasks = Task.objects.filter(organization_id=org_id).count()

    # Assigned to any user (not null)
    assigned_tasks = Task.objects.filter(organization_id=org_id, assigned_to=user).count()

    # Assigned specifically to this user
    user_assigned_tasks = Task.objects.filter(
        organization_id=org_id,
        assigned_to=user
    ).count()

    # Calculate unassigned tasks
    unassigned_tasks = total_tasks - assigned_tasks
    print("Unassigned tasks:",unassigned_tasks)

    return JsonResponse({
        'organization_id': org_id,
        'total_tasks': total_tasks,
        'assigned_tasks': assigned_tasks,
        'unassigned_tasks': unassigned_tasks,
        'user_assigned_tasks': user_assigned_tasks,
    })


# // widget 6) Assigned but not completed-----------------------------------------------------------------------------------------------------------
@login_required
def assigned_not_completed_tasks_view(request, org_id):
    try:
       
        count = Task.objects.filter(
            organization_id=org_id,
            assigned_to=request.user
        ).exclude(status='completed').count()

        return JsonResponse({
            'count': count,
            'message': 'Fetched assigned but not completed tasks'
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# // widget 8) Priority breakdown ------------------------------------------------------------------------------------------------------------------
@login_required
def priority_breakdown_view(request, org_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    # Filter by organization + assigned to current user
    tasks = Task.objects.filter(
        organization_id=org_id,
        assigned_to=request.user
    )

    # Group by priority
    priority_data = tasks.values('priority').annotate(count=Count('id'))

    # Map priorities to readable labels (optional)
    priority_map = dict(Task._meta.get_field('priority').choices)

    chart_data = {
        'labels': [],
        'data': []
    }

    for item in priority_data:
        chart_data['labels'].append(priority_map.get(item['priority'], item['priority']))
        chart_data['data'].append(item['count'])

    return JsonResponse(chart_data)