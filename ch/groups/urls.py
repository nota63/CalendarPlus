
from django.urls import path
from .views import *

urlpatterns = [

    path('groups/create/<int:org_id>/', GroupCreationWizard.as_view(), name='group_create'),

   
    path('groups/<int:org_id>/', GroupListView.as_view(), name='display_groups'),
    # send invite
    path('groups/<int:org_id>/<int:group_id>/invite/', invite_members_to_group, name='invite_members_to_group'),



  
    path('invite/<int:org_id>/<int:group_id>/<int:invitation_id>/accept/', 
        accept_or_reject_invitation, 
         name='accept_reject_invitation'),


    # Members side view for group actions 
    path('groups/user/<int:org_id>/',user_groups, name='user_groups'),

    # Manage group users
     path('groups/manage-users/<int:org_id>/<int:group_id>/',manage_group_users, name='manage_group_users'),

    #  remove the user from the group

    path('organizations/<int:org_id>/groups/<int:group_id>/remove_user/<int:user_id>/', remove_user_from_group, name='remove_user_from_group'),

    # team leader can create event within the group
    path('create_group_event/<int:org_id>/<int:group_id>/',create_group_event, name='create_group_event'),

    # display created events
    path('org/<int:org_id>/group/<int:group_id>/events/', display_group_events, name='display_group_events'),

    # Book the event

    path('organization/<int:org_id>/group/<int:group_id>/event/<int:event_id>/book/', 
      book_group_event, 
         name='book_group_event'),

    # mark as absent 
    path('organization/<int:org_id>/group/<int:group_id>/event/<int:event_id>/absent/', 
      mark_absent, 
         name='mark_absent'),


    path('organization/<int:org_id>/group/<int:group_id>/event/<int:event_id>/reminder/', 
      set_event_reminder, 
         name='set_event_reminder'),


  #  Display the users who booked the event!
    path(
        'organization/<int:org_id>/group/<int:group_id>/event/<int:event_id>/bookings/',
        fetch_event_bookings,
        name='fetch_event_bookings',
    ),

 
    path('event-analytics/<int:org_id>/<int:group_id>/<int:event_id>/', event_analytics, name='event_analytics'),
   

 
    path('user-group-event-analytics/<int:org_id>/<int:group_id>/<int:event_id>/',user_group_event_analytics, name='user_group_event_analytics'),

    path('delete_event/<int:org_id>/<int:group_id>/<int:event_id>/', delete_group_event, name='delete_group_event'),

   
    path(
        'save-recurrence/<int:org_id>/<int:group_id>/<int:event_id>/',
        SaveRecurrenceInfoView.as_view(),
        name='save_recurrence_info'
    ),

 
    path('search-events/<int:org_id>/<int:group_id>/', search_events, name='search_events'),

 
    path('group/<int:org_id>/<int:group_id>/', GroupDetailsView.as_view(), name='group_details'),

    # Group event calendar
    path('group-event-calendar/<int:org_id>/<int:group_id>/',GroupEventView.as_view(), name='group_event_calendar'),
    path('groups/<int:org_id>/<int:group_id>/<int:user_id>/group_member_details/',group_member_details, name='group_member_details'),
    # Admin side features 
    path('groups/<int:org_id>/<int:group_id>/fetch_group_members/',fetch_group_members, name='fetch_group_members'),
    path('groups/<int:org_id>/<int:group_id>/delete_group/',delete_group, name='delete_group'),
    path('groups/<int:org_id>/<int:group_id>/activities/',GroupActivityLogView.as_view(), name='activities'),
    # new features
    path('get-group-details/<int:org_id>/<int:group_id>/',fetch_group_details, name='get_group_details'),
    path('group-overview/<int:org_id>/<int:group_id>/',group_details_ajax, name='group_overview'),
    path('assign-task/',assign_task, name='assign_task'),
    path('create-group-event/',create_group_event_new, name='create_group_event'),
    path('fetch-group-events-new/',fetch_group_events_new, name='fetch_group_events_new'),
    path('fetch-bookings-new/',fetch_event_bookings_new, name='fetch_bookings_new'),
    path('invite-members-group-update/<int:org_id>/<int:group_id>/',invite_members_to_group_update, name='invite_members_group_update'),
    path('invitation-status-group-update/<int:org_id>/<int:group_id>/',invitation_status_update, name='invitation_status_group_update'),
    path('task-overview/<int:org_id>/<int:group_id>/',task_analytics_view_updated, name='task_overview'),
    

    

    



  

  
]

