from django.http import JsonResponse
from accounts.models import EventOrganization
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
            "title": event.title or "Untitled Event",
            "description": event.description,
            "start": event.created_at.isoformat(),  # TEMP: you'll change this to actual start date later
            "end": event.created_at.isoformat(),    # TEMP: same as above
            "url": f"/events/detail/{org_id}/{event.slug}/",
            "location": event.location,
            "event_type": event.event_type,
        })

    return JsonResponse(event_list, safe=False)
