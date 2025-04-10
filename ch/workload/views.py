from django.shortcuts import render,redirect,get_object_or_404
from accounts.models import Profile, Organization, MeetingOrganization
from django.contrib.auth.models import User
from group_tasks.models import Task
from django.http import JsonResponse
from django.db.models import Count, F, ExpressionWrapper, DurationField,Q
from django.db.models.functions import TruncDate, ExtractHour
from datetime import timedelta
from django.utils.timezone import now
from collections import Counter
# Create your views here.

# Categorize hour 

def categorize_hour(hour):
    if hour is None:
        return 'Unknown'
    if hour < 12:
        return 'Morning'
    elif 12 <= hour < 17:
        return 'Afternoon'
    return 'Evening'



# Display a pie chart of workload statuses

def meeting_analytics_view_widget(request, org_id):
    # Base queryset
    qs = MeetingOrganization.objects.filter(
        organization_id=org_id
        ).filter(
            Q(user=request.user) |
            Q(invitee=request.user) |
            Q(participants=request.user)
        )

    # --- 1. Count by Status ---
    by_status = qs.values('status').annotate(count=Count('id'))

    # --- 2. Count by Meeting Type ---
    by_type = qs.values('meeting_type').annotate(count=Count('id'))

    # --- 3. Count by Location ---
    by_location = qs.values('meeting_location').annotate(count=Count('id'))

    # --- 4. Daily Trend (Time Series) ---
    daily_trend = qs.annotate(day=TruncDate('meeting_date')) \
                    .values('day') \
                    .annotate(count=Count('id')) \
                    .order_by('day')

    # --- 5. Top Meeting Creators ---
    top_creators = qs.values('invitee__username') \
                     .annotate(count=Count('id')) \
                     .order_by('-count')[:5]

    # --- 6. Top Participants ---
    top_invited = User.objects.filter(participants_meetings__organization_id=org_id) \
                              .annotate(total_meetings=Count('participants_meetings')) \
                              .order_by('-total_meetings') \
                              .values('username', 'total_meetings')[:5]

    # --- 7. Time of Day Buckets ---
    hour_qs = qs.annotate(hour=ExtractHour('start_time')).values_list('hour', flat=True)
    time_buckets = Counter([categorize_hour(h) for h in hour_qs if h is not None])

    # --- 8. Meeting Duration Stats ---
    duration_qs = qs.annotate(
        duration=ExpressionWrapper(F('end_time') - F('start_time'), output_field=DurationField())
    )

    durations = [m.duration for m in duration_qs if m.duration is not None]
    avg_duration = sum(durations, timedelta()) / len(durations) if durations else timedelta()
    long_meetings_count = len([d for d in durations if d > timedelta(hours=1)])

    # --- 9. Counts for Today / Week / Month ---
    today = now().date()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    today_count = qs.filter(meeting_date=today).count()
    week_count = qs.filter(meeting_date__gte=week_start).count()
    month_count = qs.filter(meeting_date__gte=month_start).count()

    return JsonResponse({
        "status_distribution": list(by_status),
        "type_distribution": list(by_type),
        "location_distribution": list(by_location),
        "daily_trend": list(daily_trend),
        "top_creators": list(top_creators),
        "top_participants": list(top_invited),
        "time_buckets": dict(time_buckets),
        "duration": {
            "average": str(avg_duration),
            "long_meetings": long_meetings_count,
        },
        "meeting_counts": {
            "today": today_count,
            "week": week_count,
            "month": month_count,
        }
    }, safe=False)

