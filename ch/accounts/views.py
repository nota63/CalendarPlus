from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import EventOrganization, BookingOrganization
# Create your views here.


# register
# re initialized Authentication system ------------------------------------------------------------------------------------------
def register(request):
    if request.method == 'POST':
        form=UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form= UserCreationForm()    
    return render(request,'accounts/register.html',{'form':form})


# login
def login_view(request):
    if request.method == 'POST':
        form=AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user=form.get_user()
            login(request,user)
            return redirect('landing_page')
    else:
        form=AuthenticationForm()    
    return render(request,'accounts/login.html',{'form':form})


# logout
def logout_view(request):
    logout(request)
    return redirect('login')

# ----------------------------------------------------------------------------------------------------------


# Event Creation initialization
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Availability, Organization, Profile
from django.views.generic import ListView
from django.http import JsonResponse
import json
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.contrib import messages

from django.utils.dateparse import parse_date
import datetime

from django.contrib.auth.models import User
from datetime import datetime as dt
from django.urls import reverse
import datetime
from datetime import datetime, timedelta
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.text import slugify
import uuid
from django.core.exceptions import PermissionDenied



# Select Event Type
class EventTypeSelectionView(TemplateView):
    template_name = 'accounts/org_events/event_type_selection.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        org_id = self.kwargs['org_id']
        organization = get_object_or_404(Organization, id=org_id)

        # List of event types available for selection
        event_types = [
            ('one_on_one', 'One-on-One'),
            ('group', 'Group Meeting')
        ]
        
        context['organization'] = organization
        context['event_types'] = event_types
        return context

    def post(self, request, *args, **kwargs):
        org_id = self.kwargs['org_id']
        organization = get_object_or_404(Organization, id=org_id)

     
        event_type = request.POST.get('event_type')
        if event_type:
            request.session['event_type'] = event_type
            return redirect('event_details', org_id=organization.id)

        
        event_types = [
            ('one_on_one', 'One-on-One'),
            ('group', 'Group Meeting')
        ]
        
        return render(request, self.template_name, {
            'organization': organization,
            'event_types': event_types,
            'message': "Please select an event type!"
        })




# Event Details 
class EventDetailsView(TemplateView):
    template_name = 'accounts/org_events/event_details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        org_id = self.kwargs['org_id']
        organization = get_object_or_404(Organization, id=org_id)

        # Fetch the selected event type from session
        event_type = self.request.session.get('event_type')
        context['organization'] = organization
        context['event_type'] = event_type

    
        context['locations'] = [
            ('Google Meet', 'Google Meet', 'path_to_google_meet_image.jpg'),
            ('Zoom', 'Zoom', 'path_to_zoom_image.jpg'),
            ('Phone Call', 'Phone Call', 'path_to_phone_call_image.jpg'),
            ('In Person Meeting', 'In Person Meeting', 'path_to_in_person_image.jpg'),
        ]

        return context

    def post(self, request, *args, **kwargs):
        org_id = self.kwargs['org_id']
        organization = get_object_or_404(Organization, id=org_id)

       
        event_type = self.request.session.get('event_type')
        event_name = request.POST.get('event_name')
        duration = request.POST.get('duration')
        location = request.POST.get('location')
        description = request.POST.get('description')
        is_recurring = 'is_recurring' in request.POST
        buffer_time = request.POST.get('buffer_time')

      
        slug = slugify(f"{event_name}-{uuid.uuid4().hex[:8]}")

     
        event = EventOrganization(
            user=request.user,
            event_type=event_type,
            title=event_name,
            description=description,
            duration=duration,
            location=location,
            is_recurring=is_recurring,
            buffer_time=buffer_time,
            organization=organization,
            slug=slug
        )
        event.save()

      
        return redirect('event_confirmation', org_id=org_id, event_id=event.id)
       



# Final confirmation

@login_required
def event_confirmation(request, org_id, event_id):
    event = EventOrganization.objects.get(id=event_id)

  
    event_link = f"{request.scheme}://{request.get_host()}/event/{event.slug}/" 

    return render(request, 'accounts/org_events/event_confirmation.html', {
        'event': event,
        'event_link': event_link
    })



# To be modified

# Additional event operations
# display availability
# display availability
def get_availability_slots_user(request, org_id, date):
    try:
        organization = Organization.objects.get(id=org_id)
        
        # Filter availability based on user and organization
        availability = Availability.objects.filter(user=request.user, organization=organization)

        if not availability.exists():
            return JsonResponse({"error": "No availability found for this user in this organization."}, status=404)

        # Convert date to a weekday index (0=Monday, 6=Sunday)
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        day_of_week = date_obj.weekday()

        # Filter availability by day_of_week
        availability_for_day = availability.filter(day_of_week=day_of_week)

        if not availability_for_day.exists():
            return JsonResponse({"error": f"No availability found for {date_obj.strftime('%A')}."}, status=404)

        slots = []
        for available_time in availability_for_day:
            # Convert time to datetime for arithmetic
            start_time_obj = datetime.combine(datetime.today(), available_time.start_time)
            end_time_obj = datetime.combine(datetime.today(), available_time.end_time)
            interval = 30  # interval in minutes

            # Generate time slots
            while start_time_obj + timedelta(minutes=interval) <= end_time_obj:
                slot_start = start_time_obj.strftime("%H:%M")
                slot_end = (start_time_obj + timedelta(minutes=interval)).strftime("%H:%M")
                slots.append(f"{slot_start} - {slot_end}")
                start_time_obj += timedelta(minutes=interval)

        return JsonResponse({"slots": slots}, status=200)

    except Organization.DoesNotExist:
        return JsonResponse({"error": "Organization not found."}, status=404)
    except ValueError:
        return JsonResponse({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)


# edit the event!

def edit_event(request, org_id, event_slug):
    try:
        # Fetch the organization and the event using org_id and event_slug
        organization = get_object_or_404(Organization, id=org_id)
        event = get_object_or_404(EventOrganization, slug=event_slug, organization=organization)

        # Check if the request method is POST for handling the form submission
        if request.method == 'POST':
            # Get the data from the request (you'll pass this through AJAX)
            title = request.POST.get('title')
            description = request.POST.get('description')
            duration = request.POST.get('duration')
            location = request.POST.get('location')
            event_type = request.POST.get('event_type')

            # Update the event details
            event.title = title
            event.description = description
            event.duration = duration
            event.location = location
            event.event_type = event_type
            event.save()

            return JsonResponse({'success': 'Event updated successfully!'})

        # If it's a GET request, just return the current event details
        return JsonResponse({
            'event': {
                'title': event.title,
                'description': event.description,
                'duration': event.duration,
                'location': event.location,
                'event_type': event.event_type,
            }
        })

    except EventOrganization.DoesNotExist:
        return JsonResponse({'error': 'Event not found for this organization.'}, status=404)


# -------------------------------------------------------------------------------------------------------------


# Booking Event



# # Booking Page
from datetime import datetime, timedelta  

class EventBookingView(TemplateView):
    template_name = 'accounts/org_events/event_booking.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event_slug = self.kwargs['event_slug']  


        event = get_object_or_404(EventOrganization, slug=event_slug)

        
        user_profile = Profile.objects.filter(user=self.request.user, organization=event.organization).first()

        if not user_profile:
        
            raise PermissionDenied("You are not part of the same organization as the event creator.")

        context['event'] = event
        context['organization'] = event.organization

        return context





# Get available slots 
import logging

logger = logging.getLogger(__name__)
def fetch_event_user_availability(request, user_id, org_id, date):
    logger.debug(f"Fetching availability for user_id: {user_id}, org_id: {org_id}, date: {date}")
    
    # Fetch availability for the user in the organization
    availability = Availability.objects.filter(user_id=user_id, organization_id=org_id).order_by('start_time')
    
    if not availability:
        logger.error(f"No availability found for user_id: {user_id}, org_id: {org_id}")
        return JsonResponse({"error": "No availability found."}, status=404)
    
    logger.debug(f"Availability found: {availability}")
    
    # Parse the date from the URL parameter
    selected_date = parse_date(date)
    if not selected_date:
        logger.error(f"Invalid date format: {date}")
        return JsonResponse({"error": "Invalid date format."}, status=400)
    
    logger.debug(f"Selected date: {selected_date}")
    
    # Get the day of the week for the selected date
    day_of_week = selected_date.weekday()  # 0 is Monday, 6 is Sunday
    logger.debug(f"Day of the week: {day_of_week}")
    
    # Filter the availabilities for the selected day of the week
    slots = []
    for availability_item in availability:
        if availability_item.day_of_week == day_of_week:
            slot = f"{availability_item.start_time} - {availability_item.end_time}"
            slots.append(slot)
    
    # Prepare the response data
    response_data = {
        'main_time': slots  # Sending the slots in the expected format
    }
    
    return JsonResponse(response_data)



# Display Available slots 
class ScheduleEventView(TemplateView):
    template_name = 'accounts/org_events/schedule_event.html'

    def get(self, request, user_id, org_id, date, event_slug):
        user = User.objects.get(id=user_id)
        organization = Organization.objects.get(id=org_id)

        try:
            event = EventOrganization.objects.get(slug=event_slug)
        except EventOrganization.DoesNotExist:
            return JsonResponse({"error": "Event not found."}, status=404)

        try:
            date_obj = datetime.fromisoformat(date)
        except ValueError:
            return JsonResponse({"error": "Invalid date format."}, status=400)

        # Determine the day of the week
        day_of_week = date_obj.weekday()

        # Query the availability for the user and organization
        availability_slots = Availability.objects.filter(
            user=user,
            organization=organization,
            day_of_week=day_of_week,
            is_booked=False
        ).order_by('start_time')

        if not availability_slots.exists():
            return JsonResponse({"error": "No availability found for this user on the selected date."}, status=404)

        # Generate time slots for each availability
        slots = []
        interval = 30  # Interval in minutes
        for availability in availability_slots:
            start_time_obj = availability.start_time
            end_time_obj = availability.end_time

            # Create slots in 30-minute intervals
            current_time = datetime.combine(date_obj, start_time_obj)
            end_time = datetime.combine(date_obj, end_time_obj)
            while current_time + timedelta(minutes=interval) <= end_time:
                slot_start = current_time.strftime("%H:%M")
                slot_end = (current_time + timedelta(minutes=interval)).strftime("%H:%M")
                slots.append(f"{slot_start} - {slot_end}")
                current_time += timedelta(minutes=interval)

        # Handle slot selection
        selected_slot = request.GET.get('selected_slot')
        if selected_slot:
            return redirect(reverse('schedule_event_action', kwargs={
                'user_id': user_id,
                'org_id': org_id,
                'date': date,
                'event_slug': event_slug,
                'selected_slot': selected_slot,
            }))

        return render(request, self.template_name, {
            'user': user,
            'organization': organization,
            'event': event,
            'date': date,
            'time_slots': slots,
            'event_slug': event_slug,
        })






# # finally shcedule
from .models import BookingOrganization
from django.utils.dateparse import parse_time

class ConfirmEventView(TemplateView):
    template_name = 'accounts/org_events/confirm_event.html'

    def get(self, request, user_id, org_id, date, event_slug):  
        user = User.objects.get(id=user_id)
        organization = Organization.objects.get(id=org_id)
        
     
        try:
            event = EventOrganization.objects.get(slug=event_slug, organization=organization)  
        except EventOrganization.DoesNotExist:
            return redirect('error_page')  
        
        # Get the selected slot
        selected_slot = request.GET.get('selected_slot')
        if not selected_slot:
            return redirect(reverse('schedule_event', kwargs={
                'user_id': user_id,
                'org_id': org_id,
                'date': date,
                'event_slug': event_slug,  
            }))

        # Event details
        event_details = {
            'event_title': event.title,
            'event_description': event.description,
            'date': date,
            'selected_slot': selected_slot,
            'user': user,
            'organization': organization,
        }

   
        date_obj = datetime.fromisoformat(date)

       
        slot_start_time_str = selected_slot.split(' - ')[0]  
        slot_start_time = parse_time(slot_start_time_str)  

        
        booking_exists = BookingOrganization.objects.filter(
            event=event,
            start_time__date=date_obj,  
            start_time__time=slot_start_time  
        ).exists()

        return render(request, self.template_name, {
            'event_details': event_details,
            'booking_exists': booking_exists,
            'organization': organization,
            'user': user, 
            'event': event,
        })


#  finally schedule 
class ScheduleEventActionView(View):
    def post(self, request, user_id, org_id, date, event_slug): 
        user = User.objects.get(id=user_id)
        organization = Organization.objects.get(id=org_id)
        event = EventOrganization.objects.get(slug=event_slug)  

        selected_slot = request.POST.get('selected_slot')
        event_host = user  
        invitee = self.request.user 

        
        date_obj = datetime.fromisoformat(date)

       
        slot_start_time_str = selected_slot.split(' - ')[0]
        slot_start_time = parse_time(slot_start_time_str)
        slot_start = datetime.combine(date_obj, slot_start_time)

       
        slot_end = slot_start + timedelta(minutes=30)

        
        existing_booking = BookingOrganization.objects.filter(
            event=event,
            start_time__date=date_obj,
            start_time__time=slot_start_time
        ).exists()

        if existing_booking:
            messages.error(request, 'The selected time slot is already booked.')
            return redirect(reverse('schedule_event', kwargs={
                'user_id': user.id,
                'org_id': organization.id,
                'date': date,
            }))

      
        booking = BookingOrganization.objects.create(
            event=event,
            invitee=invitee,
            event_host=event_host,
            start_time=slot_start,
            end_time=slot_end,
            organization=organization,
            status='pending',  
        )

        messages.success(request, 'Your event has been scheduled successfully!')
        return redirect('org_detail', org_id=org_id)



# ------------------------------------------------------------------------------------------------------
# Display User Events

from django.core.paginator import Paginator

class UserEventsView(LoginRequiredMixin, ListView):
    template_name = "accounts/user_events/user_events.html"
    context_object_name = "events"
    paginate_by = 5 

    def get_queryset(self):
        org_id = self.kwargs.get("org_id")
        location = self.request.GET.get("location") 
        
        user_profile = get_object_or_404(Profile, user=self.request.user, organization_id=org_id)
        
 
        events = EventOrganization.objects.filter(
            organization=user_profile.organization, user=self.request.user
        )
        
     
        if location and location != 'all':
            events = events.filter(location=location)
        
  
        events_with_bookings = []
        for event in events:
            booking_count = BookingOrganization.objects.filter(event=event).count()
            events_with_bookings.append({
                "event": event,
                "booking_count": booking_count,
            })

        return events_with_bookings

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        org_id = self.kwargs.get("org_id")
        
   
        user_profile = get_object_or_404(Profile, user=self.request.user, organization_id=org_id)
        context["organization_name"] = user_profile.organization.name  
        context["org_id"] = org_id  
        
      
        events_with_bookings = self.get_queryset()
        paginator = Paginator(events_with_bookings, self.paginate_by)
        page_number = self.request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        context["page_obj"] = page_obj  
        context["events"] = page_obj.object_list 
        
        return context 


# View Bookings of the event
class ViewBookingsView(LoginRequiredMixin, ListView):
    template_name = "accounts/user_events/view_bookings.html"
    context_object_name = "bookings"

    def get_queryset(self):
        org_id = self.kwargs.get("org_id")
        event_id = self.kwargs.get("event_id")
        
       
        event = get_object_or_404(
            EventOrganization, 
            pk=event_id, 
            organization_id=org_id, 
            user=self.request.user
        )
        
   
        bookings = BookingOrganization.objects.filter(event=event).order_by("-created_at")
        return bookings

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        org_id = self.kwargs.get("org_id")
        event_id = self.kwargs.get("event_id")
        
    
        event = get_object_or_404(EventOrganization, pk=event_id, organization_id=org_id)
        context["event"] = event
        context["organization_name"] = event.organization.name
        context["org_id"] = org_id  
        return context



# Booking actions
class BookingActionView(View):
   

    def post(self, request, org_id, booking_id):
 
        organization = get_object_or_404(Organization, id=org_id)
        booking = get_object_or_404(BookingOrganization, id=booking_id, organization=organization)

       
        action = request.POST.get('action')

     
        if action == 'confirm':
            booking.confirm()
        elif action == 'cancel':
            booking.cancel()
        else:
            return HttpResponse("Invalid action")

     
        return redirect('view_bookings', org_id=organization.id, event_id=booking.event.id)
    

# Delete the event 
class DeleteEventView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/user_events/confirm_delete_event.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        org_id = self.kwargs.get("org_id")
        event_id = self.kwargs.get("event_id")
        
        organization = get_object_or_404(Organization, pk=org_id)
        event = get_object_or_404(EventOrganization, pk=event_id, organization=organization)
        
        if event.user != self.request.user:
            return redirect('error-page')  
        
        context['organization'] = organization
        context['event'] = event
        return context
    
    def post(self, request, org_id, event_id):
        org_id = self.kwargs.get("org_id")
        event_id = self.kwargs.get("event_id")
        
     
        organization = get_object_or_404(Organization, pk=org_id)
        event = get_object_or_404(EventOrganization, pk=event_id, organization=organization)
        
       
        if event.user != self.request.user:
            return redirect('error-page')  
        
     
        event.delete()
        
        return redirect('user-events',org_id=organization.id)  


# ----------------------------------------------------------------------------------------------------

# Display Bookings
class UserOrganizationBookingsView(TemplateView):
    template_name = 'accounts/user_bookings/user_bookings.html'

    def get(self, request, org_id):
   
        organization = Organization.objects.get(id=org_id)

     
        bookings = BookingOrganization.objects.filter(organization=organization, invitee=request.user)

        context = {
            'organization': organization,
            'bookings': bookings,
        }

        return render(request, self.template_name, context)
    

# Booking Detail
class BookingDetailView(View):
    def get(self, request, org_id, booking_id):
      
        booking = get_object_or_404(BookingOrganization, id=booking_id, event__organization_id=org_id)
        event = booking.event
        
  
        context = {
            'booking': booking,
            'event': event,
        }
        
        return render(request, 'accounts/user_bookings/booking_detail.html', context)
    

