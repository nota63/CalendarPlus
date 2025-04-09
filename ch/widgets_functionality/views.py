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

    try:
        group_memberships = GroupMember.objects.filter(
            user=user,
            organization_id=org_id
        ).select_related('group')

        logger.info("👥 Found %d group memberships for user %s in org %s", group_memberships.count(), user.username, org_id)

        groups = []
        for gm in group_memberships:
            logger.debug("📂 Group ID: %s, Name: %s, TL: %s", gm.group.id, gm.group.name, gm.group.team_leader)
            groups.append({
                'id': gm.group.id,
                'name': gm.group.name,
                'description': gm.group.description,
                'team_leader': gm.group.team_leader.username if gm.group.team_leader else None,
            })

        logger.info("✅ Returning %d groups to frontend.", len(groups))
        return JsonResponse({'groups': groups}, status=200)

    except Exception as e:
        logger.exception("💥 Error while fetching groups for user %s: %s", user.username, str(e))
        return JsonResponse({'error': 'An unexpected error occurred. Please try again later.'}, status=500)
