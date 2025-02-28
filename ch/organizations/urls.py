from django.urls import path
from .views import *


urlpatterns=[

    path('modify-organization/<int:org_id>/',edit_organization, name='modify_organization'),
    path('workspace-invitations/<int:org_id>/',organization_invitations, name='workspace_invitations'),
    path('customize_workspace/<int:org_id>/',customize_workspace, name='customize_workspace'),
    path('workspace-icon/<int:org_id>/',update_workspace_icon, name='workspace_icon'),
    path('workspace-status/<int:org_id>/',update_organization_status, name='workspace_status'),
    path('modify-profile/<int:org_id>/',edit_profile, name='modify_profile'),
    path('workspace_analytics/<int:org_id>/',organization_analytics, name='workspace_analytics'),
    path('workspace_details/<int:org_id>/',organization_details, name='workspace_details'),
    path('workspace_members/<int:org_id>/',fetch_organization_members, name='workspace_members'),
    path('transfer-ownership/<int:org_id>/<int:member_id>/',transfer_ownership, name='transfer_ownership'),
    path('delete-workspace/<int:org_id>/',delete_workspace, name='delete_workspace'),
    path('workspace_groups/<int:org_id>/',fetch_organization_groups, name='workspace_groups'),
    path('workspace_invitations_admin/<int:org_id>/',view_invitations, name='workspace_invitations_admin'),
    path('organizations/<int:org_id>/invitations/<int:invitation_id>/delete/', delete_invitation, name='delete_invitation'),
    path('organizations/<int:org_id>/invitations/<int:invitation_id>/extend/',extend_invitation_expiry,name='extend_invitation_expiry'),
    path('workspace_billing/<int:org_id>/',workspace_billing, name='workspace_billing'),
    path('workflows/<int:org_id>/',workflow_template, name='workflows'),
    path('hide_workspace/<int:org_id>/',hide_organization,name='hide_workspace'),
    path('duplicate-workspace/<int:org_id>/',DuplicateWorkspaceView.as_view(), name='duplicate_workspace'),
    path('pulse/<int:org_id>/',organization_pulse_view, name='pulse'),
    path('pulse_settings/<int:org_id>/',pulse_settings, name='pulse_settings'),
    path("organization/<int:org_id>/members/", handle_suspend_action, name="handle_suspend_action"),
    path("organization/<int:org_id>/suspend/<int:user_id>/<str:action>/", handle_suspend_action, name="handle_suspend_action"),
    path('create_meeting_from_nlp/<int:org_id>/',create_meeting_from_nlp, name='create_meeting_from_nlp'),
    path('meeting_analytics/<int:org_id>/',meeting_analytics, name='meeting_analytics'),
    path('create_recurring_meetings/<int:org_id>/<int:user_id>/',create_recurring_meeting, name='create_recurring_meetings'),
    path("recurring-meetings/<int:org_id>/", fetch_recurring_meetings, name="fetch_recurring_meetings"),
    path("delete-recurring-meetings/<int:org_id>/<int:meeting_id>/", delete_recurring_meeting, name="delete_recurring_meetings"),
    path('meetings-calendar-view/<int:org_id>/',get_meetings, name='meetings_calendar_view'),
    path('meeting-reminder-ajax/<int:org_id>/<int:meeting_id>/',set_meeting_reminder,name='meeting_reminder_ajax'),
    path("api/meetings/<int:org_id>/", user_meetings_api, name="user_meetings_api"),
    path("generate-embed-code/<int:org_id>/", generate_embed_code, name="generate_embed_code"),
    path('delete-all-meetings/<int:org_id>/',manage_meetings, name='delete_all_meetings'),
    path('initiate_meeting/<int:org_id>/',LaunchRoom.as_view(), name='initiate_meeting'),
    path('start_meeting/<int:org_id>/',start_meeting, name='start_meeting'),
    path('security_transport_layer/<int:org_id>/',support_transport_layer, name='security_transport_layer'),
    path("user_help_queries/<int:org_id>/", user_help_queries, name="user_help_queries"),
    path("help/query-details/<int:help_id>/", help_query_details, name="help_query_details"),
    
]


