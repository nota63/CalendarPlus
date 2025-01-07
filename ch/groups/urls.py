
from django.urls import path
from .views import *

urlpatterns = [

    path('groups/create/<int:org_id>/', GroupCreationWizard.as_view(), name='group_create'),

   
    path('groups/<int:org_id>/display/', GroupListView.as_view(), name='display_groups'),


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

    path('filter-events/<int:org_id>/<int:group_id>/', filter_events_by_location, name='filter_events_by_location'),



  
]

