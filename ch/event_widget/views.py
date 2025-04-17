from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from accounts.models import EventOrganization,BookingOrganization
from discussion_widget.views import check_access


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