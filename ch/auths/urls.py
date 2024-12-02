from django.urls import path
from . import views
from .views import *


urlpatterns=[
    path('features/',views.FeaturesImplementation.as_view(), name='features_auths'),
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

    path('organizations/<int:organization_id>/delete_profile/',views.DeleteProfileView.as_view(), name='delete_profile'),  

    # calendar part
    path('calendar_room/', views.CalendarRoomView.as_view(), name='calendar_room'),
    path('set_availability/', views.SetAvailabilityView.as_view(), name='set_availability'),

    path('manage_availability/',views.ManageAvailabilityView.as_view(), name='manage_availability'),

    # calendar
    path('calendar/', views.CalendarView.as_view(), name='calendar'),

    # actual work

    path('users/', views.OrganizationMembersWithAvailabilityView.as_view(), name='user_list'),
    path('view-user-calendar/<int:user_id>/', views.ViewUserCalendar.as_view(),name='view_user_calendar'),
    path('fetch-user-availability/<int:user_id>/', views.fetch_user_availability, name='fetch_user_availability'),
    path('schedule-meeting/', views.schedule_meeting, name='schedule_meeting'),


    # my calendar

    path('my_calendar/',views.user_calendar, name ='my_calendar'),
    path('fetch-user-meetings/', views.fetch_user_meetings, name='fetch_user_meetings'),

    # share calendar
    path('share-calendar/<int:user_id>/', ShareCalendarView.as_view(), name='share_calendar'),

    # set reminders
    path('set-reminder/<int:meeting_id>/', views.SetReminderView.as_view(), name='set_reminder'),

    # invite users in meeting
    path('invite-users/<int:meeting_id>/', MeetingInviteView.as_view(), name='invite-users'),

    # accept or reject invitations
    path('meeting_invitations/', views.InvitationListView.as_view(), name='meeting-invitations'),
    path('invitation/<int:invitation_id>/<str:action>/', views.InvitationListView.as_view(), name='invitation-action'),
    path('empty_meets/', empty_meets, name='empty_meets'),

    # analytics

    path('analytics/',AnalyticsDashboardView.as_view(), name='analytics'),

    path('select_org/',OrganizationSelectView.as_view(), name='select_org'),

    path('organization/<int:org_id>/analytics/',organization_analysis, name='organization_analytics'),

    # my events

    path('my_events/',MeetsView.as_view(),  name='my_events'),

    path('get-meet-details/', get_meet_details, name='get-meet-details'),
    path('filter-meets/',filter_meets,  name='filter-meets'),

    # create contact list

    path('intro_contacts/',IntroContacts.as_view(), name='intro_contacts'),

    path('select_contact/', ContactBookView.as_view(), name='select_contact'),

    path('contacts/', ContactListView.as_view(), name='contacts'),
    path('add-to-favorite/',add_to_favorite, name='add_to_favorite'),

    path('favorite-contacts/', views.FavoriteContactsView.as_view(), name='favorite_contacts'),
    path('remove-favorite/', views.RemoveFavoriteView.as_view(), name='remove_favorite'),  



]


     


 
   

  

   



