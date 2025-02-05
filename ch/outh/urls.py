from django.urls import path
from .views import google_calendar_connect, google,google_calendar_callback
from .views import * 


urlpatterns = [
    path('google/',google, name='google'),
    path("google-connect/", google_calendar_connect, name="google_connect"),
    path("callback/", google_calendar_callback, name="google_callback"),

    path("calendar/", google_calendar_view, name="google_calendar_view"),
    path('calendar/google_events/', get_google_events, name='google_events'),
    path('google_event_details/<str:event_id>/', get_google_event_details, name='google_event_details'),
    path('google_create_event/',create_google_event, name='google_create_event'),
    path('generate_event_report/<str:event_id>/',generate_event_report, name='generate_event_report'),
    path('google_delete_event/<str:event_id>/',delete_event, name='delete_event'),
    path('google_add_attachment/<str:event_id>/',add_event_attachment, name='google_add_attachment'),
    path('google_duplicate_event/<str:event_id>/',duplicate_event, name='google_duplicate_event'),
    path('edit_google_event/<str:event_id>/',edit_google_event, name='edit_event'),
    path('update_event_response/<str:event_id>/',update_event_response, name='update_event_response'),
    path('get_event_invite_link/<str:event_id>/',get_event_invite_link, name='get_event_invite_link'),
    path('generate_event_invite_link_for_book/<str:event_id>/',generate_google_booking_link, name='generate_event_invite_link_for_book'),
    path('publish_google_event/<str:event_id>/',publish_event, name='publish_event'),
    path('change_event_owner/<str:event_id>/',change_event_owner, name='change_event_owner'),
    path('save_custom_reminder/<str:event_id>/<str:reminder_time>/',save_custom_reminder, name='save_custom_reminder'),


]
