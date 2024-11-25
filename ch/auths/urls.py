from django.urls import path
from . import views

urlpatterns=[
    path('features/',views. FeaturesImplementation.as_view(), name='features_auths'),
    path('create_organization/',views.CreateOrganizationView.as_view(), name='create_organization'),
    path('organizations/',views.OrganizationListView.as_view(), name='organization_list'),
    path('organizations/<int:pk>/edit/',views.OrganizationEditView.as_view(), name='edit_organization'),
    path('organizations/<int:organization_id>/add-member/',views.AddMemberView.as_view(), name='add_member'),
    path('organization/<int:organization_id>/members/',views.OrganizationMembersView.as_view(), name='organization_members'),
    path('organizations/<int:organization_id>/invite/',views.InviteMemberView.as_view(), name='invite_member'),
    path('invitations/', views.ViewInvitationsView.as_view(), name='view_invitations'),
    path('invitations/respond/', views.ViewInvitationsView.as_view(), name='respond_to_invitations'),
    path('organizations/<int:organization_id>/email-invite/',views.SendEmailInvitationView.as_view(), name='send_email_invitation'),
    path('invitations/email/accept/<str:token>/',views. AcceptEmailInvitationView.as_view(), name='accept_email_invitation'),
    path('invitations/email/reject/<str:token>/', views.RejectEmailInvitationView.as_view(), name='reject_email_invitation'),
    path('organization/<int:organization_id>/invitations/',views.InvitationStatusView.as_view(), name='invitation_status'),

    path('organizations/<int:organization_id>/members/', 
         views.ActionMembersView.as_view(), 
         name='members_action'),
]


