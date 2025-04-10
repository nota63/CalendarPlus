from django.shortcuts import render
from groups.models import Group
from accounts.models import Profile, Organization, MeetingOrganization, EventOrganization, BookingOrganization
from group_tasks.models import Task
from django.db.models import Q
from django.http import JsonResponse
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