from django.urls import path
from .views import *

urlpatterns=[
    path('dm/<int:user_id>/<int:org_id>/',chat_view, name='dm'),
    path('save_message/<int:org_id>/',save_message, name='save_message'),
    path('save_file/<int:org_id>/',save_file, name='save_file'),
    path("save-code/<int:org_id>/", save_code_snippet, name="save_code_snippet"),
    path("edit-message/<int:message_id>/<int:org_id>/", edit_message, name="edit_message"),
    path('set-recurrence/<int:message_id>/<int:org_id>/',set_recurrence, name='set_recurrence'),
    path('delete_text/<int:message_id>/<int:org_id>/',delete_message, name='delete_text'),
    path('delete-all-messages/<int:conversation_id>/<int:org_id>/',delete_all_messages, name='delete_all_messages'),
    path('get-conversation-analytics/<int:conversation_id>/<int:org_id>/',get_conversation_analytics, name='get_conversation_analytics'),
    path('chat/<int:conversation_id>/repeat/<int:org_id>/modify/',handle_repeat_status, name='handle_repeat'),
    path('other-user-connections/<int:org_id>/<int:other_user_id>/',fetch_user_meetings_events, name='other_user_connections'),
    path('manage-scheduled-messages/<int:org_id>/<int:conversation_id>/', manage_scheduled_messages, name='manage_scheduled_messages'),
    path('get_message_suggestions/<int:org_id>/',get_message_suggestions, name='get_message_suggestions'),
    path('profile/<int:org_id>/',profile_view, name='profile_view'),
]
