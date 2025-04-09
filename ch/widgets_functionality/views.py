from django.shortcuts import render,redirect, get_object_or_404
from dashboard.models import DashboardWidget
from accounts.models import Organization, Profile,MeetingOrganization
from django.contrib.auth.models import User
import json
from django.utils.timezone import make_aware
from datetime import datetime
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db import models
from groups.models import Group, GroupMember
from group_tasks.models import Task
from django.db.models import Q
from django.views.decorators.http import require_GET
# ** HERE I WILL SET UP THE WIDGETS FUNCTIONALITY 


# Create your views here.

# * CALENDAR WIDGET SET-UP
# ------------------------------------------------------------------------------------------------------------------------------------------

# 1) fetch and display the meetings
import logging

logger = logging.getLogger(__name__)

@login_required
def user_meetings_json(request):
    try:
        org_id = request.GET.get('org_id')
        if not org_id:
            logger.warning("No org_id provided in request")
            return JsonResponse({'error': 'Organization ID is required'}, status=400)

        logger.debug(f"Fetching meetings for org_id: {org_id}, user: {request.user.id}")
        org = get_object_or_404(Organization, id=org_id)

        user = request.user

        # access
        profile = Profile.objects.select_related('user', 'organization').only('id').filter(user=user, organization=org).first()
        if not profile:
            return JsonResponse({'error': 'Unauthorized access'})


        meetings = MeetingOrganization.objects.filter(
            organization=org
        ).filter(
            models.Q(invitee=user) | models.Q(participants=user)
        ).distinct()

        logger.info(f"Meetings found: {meetings.count()} for user: {user.id}")

        event_list = []

        for meeting in meetings:
            logger.debug(f"Processing meeting ID: {meeting.id}")
            if meeting.meeting_date and meeting.start_time and meeting.end_time:
                try:
                    start_dt = datetime.combine(meeting.meeting_date, meeting.start_time)
                    end_dt = datetime.combine(meeting.meeting_date, meeting.end_time)

                    event = {
                        "id": meeting.id,
                        "title": meeting.meeting_title or "Untitled Meeting",
                        "start": start_dt.isoformat(),
                        "end": end_dt.isoformat(),
                        "extendedProps": {
                            "description": meeting.meeting_description if meeting.meeting_description else None,
                            "location": meeting.meeting_location if meeting.meeting_location else None,
                            "type": meeting.meeting_type if meeting.meeting_type else None,
                            "link": meeting.meeting_link if meeting.meeting_link else None,
                            "status": meeting.status if meeting.status else None,
                        }
                    }

                    logger.debug(f"Event created: {event}")
                    event_list.append(event)

                except Exception as e:
                    logger.error(f"Error combining date/time for meeting {meeting.id}: {str(e)}")
                    continue
            else:
                logger.warning(f"Missing date/time in meeting ID: {meeting.id}")

        return JsonResponse(event_list, safe=False)

    except Exception as e:
        logger.exception(f"Unexpected error fetching meetings JSON: {str(e)}")
        return JsonResponse({'error': 'Internal Server Error'}, status=500)
    


# 2) Tasks-------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Fetch and display the groups
logger = logging.getLogger(__name__)  # Set up logging

@login_required
def get_user_groups_json(request):
    org_id = request.GET.get('org_id')
    user = request.user

    logger.info("🔍 Group fetch initiated by user: %s (ID: %s)", user.username, user.id)
    logger.info("📦 Received org_id: %s", org_id)

    if not org_id:
        logger.warning("❌ Missing org_id in request.")
        return JsonResponse({'error': 'Missing org_id'}, status=400)
    
    # check access
    access=get_object_or_404(Profile,user=user,organization_id=org_id)
    if not access:
        return JsonResponse({'error:':'Unauthorized Access'},status=400)
    
    try:
        group_memberships = GroupMember.objects.filter(
            user=user,
            organization_id=org_id
        ).select_related('group', 'group__team_leader', 'group__created_by')

        logger.info("👥 Found %d group memberships for user %s in org %s", group_memberships.count(), user.username, org_id)

        groups = []
        added_group_ids = set()  # To avoid duplicates

        # ✅ Add groups where the user is a member
        for gm in group_memberships:
            group = gm.group
            if group.id not in added_group_ids:
                logger.debug("📂 (Member) Group ID: %s, Name: %s, TL: %s", group.id, group.name, group.team_leader)
                groups.append({
                    'id': group.id,
                    'name': group.name,
                    'description': group.description,
                    'team_leader': group.team_leader.username if group.team_leader else None,
                })
                added_group_ids.add(group.id)

        # ✅ Add groups where the user is a team_leader or created_by
        from groups.models import Group  # update if different model path
        extra_groups = Group.objects.filter(
            organization_id=org_id
        ).filter(
            Q(team_leader=user) | Q(created_by=user)
        ).exclude(id__in=added_group_ids)

        for group in extra_groups:
            logger.debug("📂 (Leader/Creator) Group ID: %s, Name: %s, TL: %s", group.id, group.name, group.team_leader)
            groups.append({
                'id': group.id,
                'name': group.name,
                'description': group.description,
                'team_leader': group.team_leader.username if group.team_leader else None,
            })

        logger.info("✅ Returning %d groups to frontend.", len(groups))
        return JsonResponse({'groups': groups}, status=200)

    except Exception as e:
        logger.exception("💥 Error while fetching groups for user %s: %s", user.username, str(e))
        return JsonResponse({'error': 'An unexpected error occurred. Please try again later.'}, status=500)


# 2)  Display the tasks (assigned to to request.user )
@login_required
def get_user_tasks_by_group(request):
    org_id = request.GET.get('org_id')
    group_id = request.GET.get('group_id')
    user = request.user

    logger.info("🧩 Task fetch initiated for group_id: %s and org_id: %s by user: %s", group_id, org_id, user.username)

    if not org_id or not group_id:
        logger.warning("❌ Missing org_id or group_id.")
        return JsonResponse({'error': 'Missing org_id or group_id'}, status=400)

    # check access
    access=get_object_or_404(Profile,user=user,organization_id=org_id)
    if not access:
        return JsonResponse({'error:':'Unauthorized Access'},status=400)
    

    try:
        tasks = Task.objects.filter(
            organization_id=org_id,
            group_id=group_id,
            assigned_to=user
        ).order_by('-deadline')

        logger.info("📋 Found %d tasks for group %s assigned to user %s", tasks.count(), group_id, user.username)

        task_data = []
        for task in tasks:
            task_data.append({
                'id': task.id,
                'title': task.title,
                # 'description': task.description,
                'status': task.status,
                'priority': task.priority,
                'deadline': task.deadline.strftime("%Y-%m-%d %H:%M"),
            })

        return JsonResponse({'tasks': task_data}, status=200)

    except Exception as e:
        logger.exception("💥 Error fetching tasks: %s", str(e))
        return JsonResponse({'error': 'An unexpected error occurred. Please try again later.'}, status=500)




# Display Tasks in fullcalendar
@require_GET
@login_required
def group_tasks_calendar_view(request):
    org_id = request.GET.get('org_id')
    group_id = request.GET.get('group_id')

    if not org_id or not group_id:
        return JsonResponse({'error': 'Missing org_id or group_id'}, status=400)

    organization = get_object_or_404(Organization, id=org_id)
    group = get_object_or_404(Group, id=group_id, organization=organization)

     # check access
    access=get_object_or_404(Profile,user=request.user,organization_id=org_id)
    if not access:
        return JsonResponse({'error:':'Unauthorized Access'},status=400)
    

    tasks = Task.objects.filter(group=group, organization=organization,assigned_to=request.user)

    events = []
    for task in tasks:
        if task.deadline:
            events.append({
                'id': task.id,
                'title': task.title,
                'start': task.deadline.isoformat(),
                'end': task.deadline.isoformat(),
                'allDay': True,
                'color': '#4f46e5',  # Tailwind Indigo-600 💅
            })

    return JsonResponse(events, safe=False)




