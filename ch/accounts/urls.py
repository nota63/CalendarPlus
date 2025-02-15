from django.urls import path
from . import views
from .views import *

urlpatterns=[
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),


    # Event Creation
    path('select-event-type/<int:org_id>/', EventTypeSelectionView.as_view(), name='event_type_selection'),

    path('event-details/<int:org_id>/', EventDetailsView.as_view(), name='event_details'),

    path('event/confirmation/<int:org_id>/<int:event_id>/', views.event_confirmation, name='event_confirmation'),
    # additional features
    path('get-availability-user/<int:org_id>/<str:date>/', views.get_availability_slots_user, name='get_availability_slots_user'),

    path('edit-event-neww/<int:org_id>/<slug:event_slug>/', views.edit_event, name='edit_event_neww'),


    # Display User Events

    path('events/<int:org_id>/', UserEventsView.as_view(), name='user-events'),
    # display bookings
    path("events/<int:org_id>/<int:event_id>/view-bookings/", ViewBookingsView.as_view(), name="view_bookings"),

    path('events/<int:org_id>/<int:booking_id>/action/', BookingActionView.as_view(), name='event-booking-action'),

    path('events/<int:org_id>/<int:event_id>/delete/', DeleteEventView.as_view(), name='delete-event'),

    # Booking Event

    # Event Booking
    path('event/<slug:event_slug>/', views.EventBookingView.as_view(), name='event_booking'),

    path('fetch-availability-user/<int:user_id>/<int:org_id>/<str:date>/', views.fetch_event_user_availability, name='fetch_user_availability'),


 
    path('schedule_event/<int:user_id>/<int:org_id>/<str:date>/<slug:event_slug>/', ScheduleEventView.as_view(), name='schedule_event'),
    path('confirm_event/<int:user_id>/<int:org_id>/<str:date>/<slug:event_slug>/', ConfirmEventView.as_view(), name='confirm_event'),
    path('schedule_event_action/<int:user_id>/<int:org_id>/<str:date>/<slug:event_slug>/', ScheduleEventActionView.as_view(), name='schedule_event_action'),

    #display user bookings
    path('bookings/<int:org_id>/', UserOrganizationBookingsView.as_view(), name='user_organization_bookings'),

    path('booking/<int:org_id>/<int:booking_id>/', BookingDetailView.as_view(), name='booking_detail'),






]
