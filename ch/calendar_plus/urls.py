from django.urls import path
from . import views
from .views import *


urlpatterns=[
    path('features/',views.FeaturesImplementation.as_view(), name='features_calendar'),
    # landing page
    path('landing_page/',LandingPageView.as_view(), name='landing_page'),
    path('org_detail/<int:org_id>/',OrgDetailView.as_view(),name='org_detail'),
    # edit profile
    path('organization/<int:org_id>/profile/', EditProfileView.as_view(), name='view_edit_profile'),
    path('create_organization/',views.CreateOrganizationWizardView.as_view(), name='create_organization'),
    path('organizations/',views.OrganizationListView.as_view(), name='organization_list'),
    path('organizations/<int:pk>/edit/',views.OrganizationEditView.as_view(), name='edit_organization'),
    path('organizations/<int:organization_id>/add-member/',views.AddMemberView.as_view(), name='add_member'),


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
    # project part
    path('organization/<int:org_id>/create_project/', CreateProjectView.as_view(), name='create_project'),
    path('organization/<int:org_id>/projects/', ProjectListView.as_view(), name='project_list'),
    path('organization/<int:organization_id>/project/<int:project_id>/assign_manager/', views.assign_manager_to_project, name='assign_manager_to_project'),
    path('organization/<int:organization_id>/project/<int:project_id>/manager/', views.assigned_manager_detail, name='assigned_manager_detail'),
    # View for assigning employees to a manager in the project
    path('organization/<int:organization_id>/project/<int:project_id>/manager/<int:manager_id>/assign-employees/', 
         views.assign_employee_to_manager, 
         name='assign_employee_to_manager'),
     # view project details manager and employee
    path('organization/<int:organization_id>/project/', views.view_projects, name='project_views_others'),
    path('organization/<int:organization_id>/project/<int:project_id>/details/', views.project_details, name='project_details'),
    path('project/<int:project_id>/remove_employee/<int:employee_id>/', views.remove_employee_from_project, name='remove_employee_from_project'),
    # Events
    path('event-type/', EventTypeView.as_view(), name='event_type'),
    path('select-host/', SelectEventHostView.as_view(), name='select_event_host'),
    path('create_event/',CreateEventView.as_view(),  name='create_event'),
    path('events/<int:event_id>/', views.EventDetailView.as_view(), name='event_detail'),
    path('highlighted-dates/', views.highlighted_dates, name='highlighted_dates'),
    path('user-availability-new/', views.user_availability, name='user_availability_new'),
    path('edit-event/<slug:event_slug>/', views.edit_event, name='edit_event'),
    # booking page
    path('book/<int:event_id>/', BookingPageView.as_view(), name='booking_page'),
    path('events/<int:event_id>/get_host_availability/',views.get_host_availability, name='get_availability'),
    path('book-event/<int:event_id>/', views.BookEventView.as_view(), name='book_event'),
    path('booking-confirmation/<int:booking_id>/', views.BookingConfirmationView.as_view(), name='booking_confirmation'),
    path('booking/cancel/<int:booking_id>/', views.CancelBookingView.as_view(), name='cancel_booking'),
    # events list
    path('event_list/', UserEventsView.as_view(),  name='event_list'),
    path("event/<int:pk>/details/", EventDetailsView.as_view(), name="event_details"),
    path("event/<int:pk>/bookings/", EventBookingsView.as_view(), name="event_bookings"),
    path('delete_event/<int:event_id>/',delete_event,  name='delete_event'),
    path('booking_details/<int:booking_id>/',BookingDetailsView.as_view(), name='booking_details'),
    path('cancel_booking/<int:booking_id>/', CancelBookingView.as_view(), name='cancel_booking'),
    path('booking_details_user/<int:booking_id>/', BookingDetailsViewUser.as_view(), name='booking_details_user'),
    # holiday selection
    path('holidays/',HolidaySelectionView.as_view(),  name='holidays'),
    path('create-holiday/',create_holiday, name='create_holiday'),
    path('holiday-details/<int:holiday_id>/',holiday_detail, name='holiday_details'),
    path('delete-holiday/<int:holiday_id>/', views.delete_holiday, name='delete_holiday'),

    # New availability

    path('availability/<int:organization_id>/', AvailabilityDetailView.as_view(), name='availability-detail'),



]

     


 
   

  

   



