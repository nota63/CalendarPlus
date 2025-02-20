
from django.urls import path 
from .views import *

urlpatterns = [
    path('organization/<int:org_id>/channel/',create_channel, name='create_channel'),
    path('statistics/<int:org_id>/', channel_statistics, name='channel_statistics'),
    path('organization/<int:org_id>/channels/',ChannelListView.as_view(), name='channels_list'),
    path('channel/<int:channel_id>/chat/',channel_chat, name='channel_chat'),
    path('get_organization_members/<int:organization_id>/', get_organization_members, name='get_organization_members'),
    path('channels/get_members/<int:org_id>/<int:channel_id>/',get_channel_members, name='get_channel_members'),
    path('channels/fetch_activity_logs/<int:channel_id>/<int:org_id>/', fetch_activity_logs, name='fetch_activity_logs'),
    path('channels/search/<int:org_id>/<int:channel_id>/',search_messages_links, name='search_messages_links'),
    path('channels/channel_details/<int:org_id>/<int:channel_id>/',channel_details, name='channel_details'),
    path('export_data/<int:org_id>/<int:channel_id>/', export_data, name='export_data'),
    path('channel/statistics/<int:org_id>/<int:channel_id>/', channel_statistics, name='channel_statistics'),
    path('filter_messages/<int:org_id>/<int:channel_id>/',filter_messages, name='filter_messages'),
    path('api/delete-messages/<int:org_id>/<int:channel_id>/', delete_user_messages, name='delete_user_messages'),
    path('delete_message/<int:org_id>/<int:channel_id>/<int:message_id>/',delete_message, name='delete_message'),
    path('delete_link/<int:org_id>/<int:channel_id>/<int:link_id>/',delete_link, name='delete_link'),
    path('channels/edit_message/<int:org_id>/<int:channel_id>/<int:message_id>/', edit_message, name='edit_message'),
    path('channels/edit_link/<int:org_id>/<int:channel_id>/<int:link_id>/', edit_link, name='edit_link'),
    path('channel-data/<int:org_id>/<int:channel_id>/', get_channel_data, name='channel-data'),
    path('fetch-users/<int:org_id>/<int:channel_id>/', fetch_users, name='fetch_users'),
    path('filter-by-user/<int:org_id>/<int:channel_id>/<int:user_id>/',filter_by_user, name='filter_by_user'),
    path('delete_channel_data/<int:org_id>/<int:channel_id>/',delete_channel_data, name='delete_channel_data'),
    path('ban-user/<int:org_id>/<int:channel_id>/<int:user_id>/',ban_user, name='ban_user'),
    # Fetch organizations where the user is an admin
    path('fetch-admin-organizations/<int:org_id>/<int:channel_id>/', 
         fetch_admin_organizations, 
         name='fetch_admin_organizations'),
    
    # Grant access to a selected organization
    path('grant-channel-access/<int:org_id>/<int:channel_id>/<int:selected_org_id>/', 
         grant_channel_access, 
         name='grant_channel_access'),

    path('set_retention_policy/<int:org_id>/<int:channel_id>/',set_retention_policy, name='set_retention_policy'),
    path('pin-message/<int:org_id>/<int:channel_id>/<int:message_id>/', pin_message, name='pin_message'),  
    path('toggle_star_message/<int:org_id>/<int:channel_id>/<int:message_id>/', toggle_star_message, name='toggle_star_message'),
    path('reply/<int:org_id>/<int:channel_id>/<int:message_id>/', handle_reply, name='handle_reply'),
    path('message_recurring/<int:org_id>/<int:channel_id>/<int:message_id>/',set_recurring_message, name='message_recurring'),
        # Monitor Recurring Messages
    path('monitor-recurring-messages/<int:org_id>/<int:channel_id>/',monitor_recurring_messages, name='monitor_recurring_messages'),

    # Delete Recurring Message
    path('delete-recurring-message/<int:recurring_message_id>/',delete_recurring_message, name='delete_recurring_message'),
      # URL to fetch all flagged messages
    path('fetch-flagged-messages/<int:org_id>/<int:channel_id>/',fetch_flagged_messages, name='fetch_flagged_messages'),

    # URL to warn the user who flagged a message
    path('warn-user/<int:message_id>/', warn_user, name='warn_user'),
    path('channels/<int:org_id>/save/<int:channel_id>/',save_event_data, name='save_event_data'),
    path('events/fetch/<int:org_id>/<int:channel_id>/',fetch_event_details, name='fetch_event_details'),
    path('mark_attending/<int:org_id>/<int:channel_id>/<int:event_id>/',mark_attending, name='mark_attending'),
    path('channel_settings/<int:org_id>/<int:channel_id>/',channel_settings_view, name='channel_settings'),
    path('channel_events/<int:org_id>/<int:channel_id>/',channel_events_calendar, name='channel_events'),

    # Channel list features
    path('delete-channel/<int:org_id>/<int:channel_id>/',delete_channel, name='delete_channel'),
    path('export-channel-data/<int:org_id>/<int:channel_id>/',export_channel_data, name='export_channel_data'),
    path('manage-channel-access/<int:channel_id>/',manage_channel_access, name='manage_channel_access'),
    path('manage-user-permissions/<int:org_id>/<int:channel_id>/<int:user_id>/',manage_user_permissions, name='manage_use_permissions'),
    path('api/manage_banned_users/<int:org_id>/<int:channel_id>/',manage_banned_users, name='manage_banned_users'),
    path('send-alert-notification/<int:org_id>/<int:channel_id>/', send_alert_notification, name='send_alert_notification'),
    path('notifications/<int:org_id>/<int:channel_id>/', fetch_channel_notifications, name='fetch_notifications'),
    path('notifications/mark-read/<int:alert_id>/', mark_notification_as_read, name='mark_notification_read'),
    path('schedule-alert/<int:org_id>/<int:channel_id>/',schedule_alert, name='schedule_alert'),
    path('fetch_scheduled_alerts/<int:org_id>/<int:channel_id>/',fetch_scheduled_alerts, name='fetch_scheduled_alerts'),
    path('unschedule_alert/',unschedule_alert, name='unschedule_alert'),
    path('manage-activities/<int:org_id>/<int:channel_id>/',fetch_activities, name='manage_activities'),
    path('clear-activities/<int:org_id>/<int:channel_id>/',clear_activities, name='clear_activities'),
]
