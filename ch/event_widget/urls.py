from django.urls import path
from .views import *

urlpatterns = [
    path('user-events-calendar/<int:org_id>/',user_events_for_calendar, name='user_events_calendar'),
    path('event-detail-widget/<int:org_id>/<slug:event_slug>/',event_detail_with_bookings, name='event_detail_with_bookings'),
    path('team-availability-heatmap/<int:org_id>/',get_team_availability_heatmap, name='team_availability_heatmap'),
    path('workload-distribution/<int:org_id>/',workload_distribution_view, name='workload_distribution'),


]