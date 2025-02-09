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
     # Fetch all members and check suspension status
    path("organization/<int:org_id>/members/", handle_suspend_action, name="handle_suspend_action"),
    
    # Handle ban/unban actions
    path("organization/<int:org_id>/suspend/<int:user_id>/<str:action>/", handle_suspend_action, name="handle_suspend_action"),
    
]


