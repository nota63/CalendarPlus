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
                            "description": meeting.meeting_description,
                            "location": meeting.meeting_location,
                            "type": meeting.meeting_type,
                            "link": meeting.meeting_link,
                            "status": meeting.status,
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