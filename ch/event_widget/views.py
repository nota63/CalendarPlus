from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from accounts.models import EventOrganization,BookingOrganization,Availability,Organization,Profile,MeetingOrganization
from discussion_widget.views import check_access
from collections import defaultdict
import datetime
from group_tasks.models import Task
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime, timedelta
from django.utils.timezone import now
from django.db.models import Q, Prefetch
from django.contrib.auth.models import User
# SET UP LOGGER
import logging
logger = logging.getLogger(__name__)



def user_events_for_calendar(request, org_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    events = EventOrganization.objects.filter(
        organization_id=org_id,
        user=request.user
    ).order_by('-created_at')

    event_list = []

    for event in events:
        # Assuming you'll calculate the start and end dynamically in the frontend or later
        event_list.append({
            "id": event.id,
            'slug':event.slug,
            "title": event.title or "Untitled Event",
            "description": event.description,
            "start": event.created_at.isoformat(),  # TEMP: you'll change this to actual start date later
            "end": event.created_at.isoformat(),    # TEMP: same as above
            "url": f"/events/detail/{org_id}/{event.slug}/",
            "location": event.location,
            "event_type": event.event_type,
        })

    return JsonResponse(event_list, safe=False)


# fetch event related bookings and event details
def event_detail_with_bookings(request, org_id, event_slug):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    # Fetch the event
    event = get_object_or_404(
        EventOrganization,
        organization_id=org_id,
        slug=event_slug,
        user=request.user  # Ensure the user is the host
    )

    # Fetch bookings for this event
    bookings = BookingOrganization.objects.filter(
        organization_id=org_id,
        event=event
    ).select_related('invitee').order_by('-start_time')

    # Prepare event data
    event_data = {
        'title': event.title,
        'description': event.description,
        'event_type': event.event_type,
        'location': event.location,
        'duration': event.duration,
        'is_recurring': event.is_recurring,
        'created_at': event.created_at.strftime('%Y-%m-%d %H:%M'),
    }

    # Prepare booking data
    booking_list = []
    for booking in bookings:
        booking_list.append({
            'invitee': booking.invitee.get_full_name() or booking.invitee.username,
            'status': booking.status,
            'start_time': booking.start_time.strftime('%Y-%m-%d %H:%M'),
            'end_time': booking.end_time.strftime('%Y-%m-%d %H:%M'),
        })

    return JsonResponse({
        'event': event_data,
        'bookings': booking_list
    })

# Widget 2) Team availability Heatmap------------------------------------------------------------------------------------------------------------

def get_team_availability_heatmap(request, org_id):
    organization = get_object_or_404(Organization, id=org_id)

    # Get users in the organization
    profiles = Profile.objects.filter(organization=organization).select_related('user')
    users = [profile.user for profile in profiles]

    # Build data structure: { user_id: { day: [slot, slot, ...] } }
    heatmap_data = []

    for profile in profiles:
        user = profile.user
        user_data = {
            "user_id": user.id,
            "full_name": profile.full_name or user.get_full_name(),
            "profile_picture": profile.profile_picture.url if profile.profile_picture else None,
            "availability": defaultdict(list),  # 0 to 6 -> slots
        }

        user_availabilities = Availability.objects.filter(
            user=user,
            organization=organization
        )

        for slot in user_availabilities:
            user_data["availability"][slot.day_of_week].append({
                "start_time": slot.start_time.strftime('%H:%M'),
                "end_time": slot.end_time.strftime('%H:%M'),
                "is_booked": slot.is_booked,
            })

        # Convert defaultdict to dict before appending
        user_data["availability"] = dict(user_data["availability"])
        heatmap_data.append(user_data)

    return JsonResponse({
        "organization": {
            "id": organization.id,
            "name": organization.name,
        },
        "heatmap": heatmap_data,
        "days_of_week": ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
    }, safe=False)


# // Widget 3) Workload Distributions-------------------------------------------------------------------------------------------------------------------

def get_week_range():
    today = now().date()
    start = today - timedelta(days=today.weekday())  # Monday
    end = start + timedelta(days=6)  # Sunday
    return start, end

def calculate_duration(start_time, end_time):
    dt1 = datetime.combine(now().date(), start_time)
    dt2 = datetime.combine(now().date(), end_time)
    return max((dt2 - dt1).total_seconds() / 3600, 0)

def workload_distribution_view(request, org_id):
    try:
        logger.info(f"[WorkloadWidget] Fetching workload distribution for org_id={org_id}")

        start, end = get_week_range()
        logger.debug(f"[WorkloadWidget] Week range: {start} to {end}")

        profiles = Profile.objects.filter(organization_id=org_id).select_related("user")
        users = [p.user for p in profiles]

        logger.info(f"[WorkloadWidget] Found {len(users)} users for org {org_id}")

        tasks = Task.objects.filter(
            assigned_to__in=users,
            deadline__range=(start, end),
            organization_id=org_id  # ✅ Scoped to org
        )

        meetings = MeetingOrganization.objects.filter(
            Q(user__in=users) | Q(invitee__in=users),
            meeting_date__range=(start, end),
            organization_id=org_id  # ✅ Scoped to org
        ).prefetch_related('invitee')

        availabilities = Availability.objects.filter(
            user__in=users,
            organization_id=org_id,
            is_booked=False
        )

        # Organize data
        task_map, meeting_map, availability_map = {}, {}, {}

        for task in tasks:
            uid = task.assigned_to_id
            task_map.setdefault(uid, []).append(task)

        for meeting in meetings:
            try:
                participant_ids = set([meeting.user_id] + list(meeting.invitees.values_list("id", flat=True)))
                for uid in participant_ids:
                    meeting_map.setdefault(uid, []).append(meeting)
            except Exception as e:
                logger.warning(f"[WorkloadWidget] Failed to map meeting participants: {e}")

        for a in availabilities:
            availability_map.setdefault(a.user_id, []).append(a)

        logger.info("[WorkloadWidget] Data mapping complete, computing stats")

        data = []
        for profile in profiles:
            user = profile.user
            uid = user.id

            try:
                # TASK HOURS
                user_tasks = task_map.get(uid, [])
                task_hours = sum([getattr(task, "estimated_hours", 1) or 1 for task in user_tasks])

                # MEETING HOURS
                user_meetings = meeting_map.get(uid, [])
                meeting_hours = 0
                for m in user_meetings:
                    meeting_hours += calculate_duration(m.start_time, m.end_time)

                # AVAILABILITY HOURS
                user_avail = availability_map.get(uid, [])
                available_hours = sum([calculate_duration(a.start_time, a.end_time) for a in user_avail])

                remaining_capacity = max(available_hours - (task_hours + meeting_hours), 0)

                data.append({
                    "user_id": uid,
                    "user_name": user.get_full_name() or user.username,
                    "task_hours": round(task_hours, 2),
                    "meeting_hours": round(meeting_hours, 2),
                    "available_hours": round(available_hours, 2),
                    "remaining_capacity": round(remaining_capacity, 2),
                })

            except Exception as user_err:
                logger.error(f"[WorkloadWidget] Error processing user ID {uid}: {user_err}")

        # Sort and suggest
        recommended = sorted(data, key=lambda x: x["remaining_capacity"], reverse=True)
        suggested_user = recommended[0] if recommended else None

        logger.info(f"[WorkloadWidget] Returning {len(recommended)} user stats")

        return JsonResponse({
            "status": "success",
            "organization_id": org_id,
            "week_range": {"start": str(start), "end": str(end)},
            "data": recommended,
            "recommended_user": suggested_user
        })

    except ObjectDoesNotExist:
        logger.exception(f"[WorkloadWidget] ObjectDoesNotExist: Invalid org_id={org_id}")
        return JsonResponse({"status": "error", "message": "Invalid organization or user mapping."}, status=400)

    except Exception as e:
        logger.exception(f"[WorkloadWidget] Unexpected error for org_id={org_id}")
        return JsonResponse({"status": "error", "message": str(e)}, status=500)