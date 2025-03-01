from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Meeting
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import MeetingForm
from django.db.models import Count, Avg, Max, Min
from datetime import timedelta
from django.utils import timezone
from .models import Meeting
import json
from django.db.models.functions import ExtractHour
# essentials
from django.views import View
from django.http import JsonResponse
from .models import Meeting
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from accounts.models import Profile, Availability, Organization



# render a calender

class RenderCalendarView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'meet/render_calender.html')

class CreateMeetingView(LoginRequiredMixin, View):
    def post(self, request):
        title = request.POST.get('title')
        date = request.POST.get('date')
        time = request.POST.get('time')
        meeting_link=request.POST.get('meeting_link')
        user_id = request.POST.get('user_id')
        meeting_type=request.POST.get('meeting_type')
        admin = request.user
        user = User.objects.get(id=user_id)
        user_email=user.email
        meeting = Meeting(meeting_type=meeting_type,title=title, date=date, time=time, user=user, admin=admin,meeting_link=meeting_link)
        meeting.save()

        context={
            'user_id':user_id,
            'user':user,
            'meeting_type':meeting_type,
            'meeting_link':meeting_link,
            'title':title,
            'date':date,
            'time':time,
            'admin':admin
        }

 
        subject=f'You Have New Meeting With {request.user}'
        from_email=settings.DEFAULT_FROM_EMAIL
        recipient_list=[user_email]
        html_message=render_to_string('meet/email_backend.html',context)
        plain_message='New Meeting Received!'

        try:
          send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=recipient_list,
            html_message=html_message
          )
        except Exception as e:
            return JsonResponse({'exeption':str(e)})
        return JsonResponse({'status': 'success'})

class FetchAvailabilityView(LoginRequiredMixin, View):
    def get(self, request):
        # Get the organization IDs of the logged-in user
        user_profiles = Profile.objects.filter(user=request.user)
        organization_ids = user_profiles.values_list('organization_id', flat=True)

        # Fetch availability for users belonging to the same organizations
        availabilities = Availability.objects.filter(user__profiles__organization_id__in=organization_ids)

        # Get today's date to base the week on
        today = timezone.localdate()

        # Prepare the availability data for FullCalendar
        events = []
        for availability in availabilities:
            # Find the next matching day in the week
            days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            current_day_index = days_of_week.index(today.strftime('%A'))  # Get the current day of the week as index
            target_day_index = days_of_week.index(availability.day_of_week)  # Day of week from availability

            # Calculate the difference between today and the target day
            days_diff = target_day_index - current_day_index
            if days_diff <= 0:
                days_diff += 7  # Ensure we're looking at the next week if the day already passed

            # Get the target date for the availability
            target_date = today + timedelta(days=days_diff)

            # Create datetime objects for the start and end times
            start_datetime = datetime.combine(target_date, availability.start_time)
            end_datetime = datetime.combine(target_date, availability.end_time)

            # Convert to ISO 8601 format (FullCalendar uses this format)
            start_iso = start_datetime.isoformat()
            end_iso = end_datetime.isoformat()

            events.append({
                'id': availability.id,
                'title': f"{availability.user.username} - {availability.start_time} to {availability.end_time}",
                'start': start_iso,  # Use the correctly formatted datetime
                'end': end_iso,      # Use the correctly formatted datetime
                'allDay': False,     # Not an all-day event
                'backgroundColor': "#28a745",  # Customize as needed (Green for availability)
                'borderColor': "#28a745",      # Customize as needed
                'isAvailability': True,  # Custom attribute to indicate it's availability
            })
        
        return JsonResponse({'events': events})
    
class GetMeetingsView(LoginRequiredMixin, View):
    def get(self, request):
        start = request.GET.get('start')
        end = request.GET.get('end')
        meeting_type = request.GET.get('meeting_type', 'all')

        meetings = Meeting.objects.filter(
            Q(admin=request.user) | Q(user=request.user),
            date__range=[start, end]
        )

        if meeting_type != 'all':
            meetings = meetings.filter(meeting_type=meeting_type)

        events = []
        for meeting in meetings:
            event_start = f"{meeting.date}T{meeting.time}"
            event_end = (meeting.date + timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M')
        

            events.append({
                'title': meeting.title,
                'meeting_link': meeting.meeting_link,
                'start': event_start,
                # new
                'admin': meeting.admin.username if meeting.admin else 'No admin assigned',
                'end': event_end,
                'user': meeting.user.username,
                'meeting_type': meeting.meeting_type,
                'allDay': False  
            })

        return JsonResponse(events, safe=False)
    
# get users of same organization
class GetUsersView(LoginRequiredMixin, View):
    def get(self, request):
        # Get the organizations the logged-in user belongs to
        user_profiles = Profile.objects.filter(user=request.user)
        organization_ids = user_profiles.values_list('organization_id', flat=True)

        # Fetch users belonging to the same organizations
        users = User.objects.filter(profiles__organization_id__in=organization_ids).distinct()
        user_list = [{'id': user.id, 'username': user.username} for user in users]
        
        return JsonResponse({'users': user_list})


from .forms import UpdateEmailForm
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

@login_required
def update_email(request):
    if request.method == 'POST':
        form =UpdateEmailForm(request.POST,request.FILES,instance=request.user,)
        if form.is_valid():
            try:
                form.save()
                from_email=settings.DEFAULT_FROM_EMAIL
                recipients_list=[request.user.email]
                subject='Email Has Been Updated !'
                html_message=render_to_string('meet/email_updated.html')
                plain_message='Your Email Has Been Updated'

                try:
                  send_mail(
                    subject=subject,
                    message=plain_message,
                    from_email=from_email,
                    recipient_list=recipients_list,
                    html_message=html_message
                    )
                except Exception as e:
                    return JsonResponse({'exception':str(e)}, status=400)
                messages.success(request,f'Thank You {request.user} Your Email Updated Successfully')
                return redirect('done')
            except Exception as e:
                return JsonResponse({'exception':str(e)}, status=400)
    else:
        form= UpdateEmailForm()
    instance=request.user            
    return render(request,'meet/update_email.html',{"form":form, 'instance':instance})

def done(request):
    return render(request,'meet/done.html')

def get_profile_info(request):
    print("User data:", request.user)
    me=request.user
    return render(request,'meet/profile_info.html',{'me':me})


# fetch device info
import psutil
import socket

import pyautogui
import os
from datetime import datetime
import os
import pyautogui
from datetime import datetime
from django.http import JsonResponse
from django.views import View 


class TakeScreenshotView(View):
    def get(self, request):

        gallery_path = os.path.join(settings.MEDIA_ROOT, 'screenshots')
        os.makedirs(gallery_path, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        screenshot_filename = f'screenshot_{timestamp}.png'
        screenshot_path = os.path.join(gallery_path, screenshot_filename)

        screenshot = pyautogui.screenshot()
        screenshot.save(screenshot_path)

        relative_path = f'screenshots/{screenshot_filename}'
        full_url = f"{settings.MEDIA_URL}{relative_path}"

        return render(request, 'meet/screenshot_display.html', {'screenshot_url': full_url})
    
# essential imports..
from django.db.models import Q
from datetime import timedelta

class GetMeetingsView(LoginRequiredMixin, View):
    def get(self, request):
        start = request.GET.get('start')
        end = request.GET.get('end')
        meeting_type = request.GET.get('meeting_type', 'all')

        meetings = Meeting.objects.filter(
            Q(admin=request.user) | Q(user=request.user),
            date__range=[start, end]
        )

        if meeting_type != 'all':
            meetings = meetings.filter(meeting_type=meeting_type)

        events = []
        for meeting in meetings:
            event_start = f"{meeting.date}T{meeting.time}"
            event_end = (meeting.date + timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M')
        

            events.append({
                'title': meeting.title,
                'meeting_link': meeting.meeting_link,
                'start': event_start,
                # new
                'admin': meeting.admin.username if meeting.admin else 'No admin assigned',
                'end': event_end,
                'user': meeting.user.username,
                'meeting_type': meeting.meeting_type,
                'allDay': False  
            })

        return JsonResponse(events, safe=False)
    
       
def user_meetings(request):
    meetings=Meeting.objects.filter(user=request.user)
    return render(request,'meet/user_meetings.html',{'meetings':meetings}) 



# analytics section


def analytics_view(request):
    user = request.user  
    today = timezone.now().date()

    total_meetings = Meeting.objects.filter(user=user).count()

    meeting_count_by_type = (
        Meeting.objects.filter(user=user)
        .values('meeting_type')
        .annotate(count=Count('id'))
    )

    week_start = today - timedelta(days=today.weekday())
    meetings_this_week = (
        Meeting.objects.filter(user=user, date__gte=week_start)
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )

    peak_hours = (
        Meeting.objects.filter(user=user)
        .annotate(hour=ExtractHour('time'))
        .values('hour')
        .annotate(count=Count('id'))
        .order_by('hour')
    )

    daily_meetings = (
        Meeting.objects.filter(user=user, date__gte=today - timedelta(days=30))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )

    context = {
        'total_meetings': total_meetings,
        'meeting_count_by_type_json': json.dumps(list(meeting_count_by_type)),
        'meetings_this_week_json': json.dumps([
            {'date': item['date'].isoformat(), 'count': item['count']} for item in meetings_this_week
        ]),
        'peak_hours_json': json.dumps(list(peak_hours)),
        'daily_meetings_json': json.dumps([
            {'date': item['date'].isoformat(), 'count': item['count']} for item in daily_meetings
        ]),
    }
    
    return render(request, 'meet/analytics.html', context)


# fetch device info
import psutil
import socket

def device_info_view(request):
    system_name = socket.gethostname()
    system_info = {
        'system_name':system_name,
        'cpu_usage': psutil.cpu_percent(interval=1),
        'memory_info': psutil.virtual_memory(),
        'disk_usage': psutil.disk_usage('/'),
        'network_info': psutil.net_io_counters(),
        'battery': psutil.sensors_battery()  
    }
    if system_info['battery']:
        battery_percent = system_info['battery'].percent
        power_plugged = system_info['battery'].power_plugged
        time_left = system_info['battery'].secsleft if system_info[
                                                           'battery'].secsleft != psutil.POWER_TIME_UNLIMITED else None
    else:
        battery_percent = power_plugged = time_left = None

    context = {
        'system_name':system_name,
        'cpu_usage': system_info['cpu_usage'],
        'total_memory': system_info['memory_info'].total / (1024 ** 3),
        'used_memory': system_info['memory_info'].used / (1024 ** 3),
        'memory_percent': system_info['memory_info'].percent,
        'total_disk': system_info['disk_usage'].total / (1024 ** 3),
        'used_disk': system_info['disk_usage'].used / (1024 ** 3),
        'disk_percent': system_info['disk_usage'].percent,
        'bytes_sent': system_info['network_info'].bytes_sent / (1024 ** 2),
        'bytes_recv': system_info['network_info'].bytes_recv / (1024 ** 2),
        'battery_percent': battery_percent,
        'power_plugged': power_plugged,
        'time_left': time_left,
    }
    return render(request, 'meet/device_info.html', context)


# USER MEETING COUNT
from django.db.models import Count, Q,F
from django.views import View
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import TruncMonth
from django.core.paginator import Paginator


class IntroAnalysisView(View):

    template_name='meet/intro.html'
    def get(self, request):
        return render(request,self.template_name)
    


class MeetingCountView(View):
    template_name = 'meet/count.html'

    def get(self, request):
        top_users = (
            User.objects.annotate(meeting_count=Count('meeting')).order_by('-meeting_count')[:4]
        )

        # Prepare top 4 users details
        top_1_users = []
        for rank, user in enumerate(top_users, start=1):
            top_1_users.append({
                'rank': rank,
                'username': user.username,
                'meeting_count': user.meeting_count
            })

        # Find the user with the most active days (distinct meeting dates)
        most_active_user = (
            User.objects.annotate(active_days=Count('meeting__date', distinct=True)).order_by('-active_days').first()
        )

        # Prepare most active user details
        top_active_user = []
        if most_active_user:
            top_active_user.append({
                'username': most_active_user.username,
                'active_days': most_active_user.active_days
            })

        # Meeting types breakdown for each user
        users_meeting_type_count = User.objects.annotate(
            task_meetings=Count('meeting', filter=Q(meeting__meeting_type='Task')),
            standup_meetings=Count('meeting', filter=Q(meeting__meeting_type='Standup')),
            personal_meetings=Count('meeting', filter=Q(meeting__meeting_type='Personal')),
            team_meetings=Count('meeting', filter=Q(meeting__meeting_type='Team'))
        )

        meeting_type_breakdown = []
        for user in users_meeting_type_count:
            meeting_type_breakdown.append({
                'username': user.username,
                'Task': user.task_meetings,
                'Standup': user.standup_meetings,
                'Personal': user.personal_meetings,
                'Team': user.team_meetings
            })

        current_time = timezone.now()
        one_week_from_now = current_time + timedelta(days=7)

        upcoming_meetings = Meeting.objects.filter(
            date__gte=current_time, date__lte=one_week_from_now
        ).select_related('user')

        # Prepare a list of users with upcoming meetings
        upcoming_meetings_users = [
            {
                'User': meeting.user.username,
                'Meeting_Title': meeting.title,
                'Date': meeting.date
            }
            for meeting in upcoming_meetings
        ]

        inactive_users=User.objects.filter(meeting__isnull=True)
        
        # prepare a tuple dict 
        inactive=({
            'user':user.username
        }
        for user in inactive_users
        )
        meeting_time_distribution = (
          Meeting.objects
         .values_list('time', flat=True)
         )

       # Prepare a dictionary for time distribution
        time_distribution = {}
        for meeting_time in meeting_time_distribution:
         hour = meeting_time.hour 
        time_distribution[hour] = time_distribution.get(hour, 0) + 1
        time_distribution_list = [
         {'hour': f"{hour:02d}:00", 'meetings_count': count}
         for hour, count in sorted(time_distribution.items(), key=lambda x: x[1], reverse=True)
         ]
        
        # get the user with most meetings as an admin

        most_frequent_meeting_admin=(
            User.objects.annotate(admin_meeting_count=Count('admin_user')).order_by('-admin_meeting_count').first()


        )
        frequent_admin_meetings=[

        ]
        if most_frequent_meeting_admin:
            frequent_admin_meetings.append({
                'top_admin':most_frequent_meeting_admin.username,
                'admin_meetings_count':most_frequent_meeting_admin.admin_meeting_count
            })

        all_meeting_types = ['Task', 'Standup', 'Personal', 'Team']
        users_with_all_types = (
          User.objects.annotate(
            meeting_types=Count('meeting__meeting_type', distinct=True)
         )
         .filter(meeting__meeting_type__in=all_meeting_types)
        .filter(meeting_types=len(all_meeting_types))
    )

        all_type_users = [{
         'user': user.username
        } for user in users_with_all_types]

        today=timezone.now().date()
        week_start= today - timedelta(days=today.weekday())

        user_meeting_frequency = (
            User.objects.annotate(meeting_count=Count('meeting',filter=Q(meeting__date__gte=week_start))).order_by('-meeting_count')
        )

        users_frequency=[{
            'user':user.username,
            'meetings_this_week':user.meeting_count

        }for user in user_meeting_frequency]

        last_month=timezone.now().date()- timedelta(days=30)

        active_users_last_month=(
            User.objects.annotate(meeting_count=Count('meeting',filter=Q(meeting__date__gte=last_month))).order_by('-meeting_count')
        )

        # prepare it
        last_month_actives=[{
            'user':user.username,
            'meetings_in_last_month':user.meeting_count

        } for user in active_users_last_month]

        
        overlapping_meetings = Meeting.objects.filter(
            Q(user=F('user'))& Q(time__lt=F('time'))
        )

        overlapping=[{
            'user':meeting.user.username,
            'overlapping_meeting':meeting.title

        } for meeting in overlapping_meetings]

        # popular meeting links
        popular_meeting_links = (
            Meeting.objects.values('meeting_link').annotate(link_count=Count('id')).order_by('-link_count')
        )

        famous_meeting_links=[{
            'meeting_link':entry['meeting_link'],
            'usage_count':entry['link_count']

        } for entry in popular_meeting_links]

         # Group meetings by month and year, and count the number of meetings
        monthly_meetings = (
          Meeting.objects.annotate(month=TruncMonth('date'))  
         .values('user__username', 'month')  
         .annotate(meeting_count=Count('id'))  
         .order_by('month')  
      )
        user_month_meetings = [{
         'user': entry['user__username'],  
         'month': entry['month'],
        'meetings': entry['meeting_count']
        } for entry in monthly_meetings]

        """
         User's Meeting Participation in Specific Meeting Types
         track how much each user participates in specific meeting types 
        """
        user_meeting_types = (
         User.objects.annotate(
            task_meetings=Count('meeting', filter=Q(meeting__meeting_type='Task')),
            standup_meetings=Count('meeting', filter=Q(meeting__meeting_type='Standup')),
            personal_meetings=Count('meeting', filter=Q(meeting__meeting_type='Personal')),
            team_meetings=Count('meeting', filter=Q(meeting__meeting_type='Team'))
          )
        )

    # Paginate the queryset
        paginator = Paginator(user_meeting_types,2)  
        page_number = request.GET.get('page')
        page_objs = paginator.get_page(page_number)
        users_meeting_types = [{
        'user': user.username,
        'task': user.task_meetings,
        'standup': user.standup_meetings,
        'personal': user.personal_meetings,
        'team': user.team_meetings
        } for user in page_objs]

        """find users who has meetings that overlap in time (within the same day)"""
        conflicting_users = (
          Meeting.objects.values('date', 'time', 'user__username')  # 'user__username' gets the username
          .annotate(user_count=Count('user', filter=Q(user__meeting__time__gte=F('time'))))
          .filter(user_count__gt=1)
          .order_by('date', 'time')
      )
        paginator_conflicts = Paginator(conflicting_users, 2)  # 2 entries per page (you can change it)
        page_number = request.GET.get('page')
        page_objs_conflicts = paginator_conflicts.get_page(page_number)
        send_conflicts = [{
        'date': entry['date'],
        'time': entry['time'],
        'conflicting_users_count': entry['user_count'],
        'username': entry['user__username'] 
         } for entry in page_objs_conflicts]

        context = {
            'top_1_users': top_1_users,
            'top_active_user': top_active_user,
            'meeting_type_breakdown': meeting_type_breakdown,
            'upcoming_meeting_users':upcoming_meetings_users,
            'inactive':inactive,
            'time_distribution':time_distribution_list,
            'frequent_admin_meetings':frequent_admin_meetings,
            'all_type_users':all_type_users,
            'users_frequency':users_frequency,
            'last_month_actives':last_month_actives,
            'overlapping':overlapping,
            'meeting_links':famous_meeting_links,
            'month_meetings':user_month_meetings,
            'meeting_types':users_meeting_types,
            'page_obj':page_objs,
            'send_conflicts':send_conflicts,
            'page_objs_conflicts':page_objs_conflicts
        }

        return render(request, self.template_name, context)
    





# API SECTION

# some imports
from .serializers import MeetingSerializer
from .models import Meeting
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAdminUser
from .pagination import MyCustomPagination
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

# meeting set
class MeetingSet(viewsets.ModelViewSet):
    queryset=Meeting.objects.all()
    serializer_class=MeetingSerializer
    pagination_class=MyCustomPagination
    authentication_classes=[SessionAuthentication]
    permission_classes=[IsAdminUser]
    throttle_classes=[UserRateThrottle]

    def perform_create(self, serializer):
        meeting=serializer.save(admin=self.request.user)
    
        context={
            'user_id':meeting.user_id,
            'user':meeting.user,
            'meeting_type':meeting.meeting_type,
            'meeting_link':meeting.meeting_link,
            'title':meeting.title,
            'date':meeting.date,
            'time':meeting.time,
            'admin':meeting.admin
        }
        subject=f'You Have New Meeting With {self.request.user}'
        from_email=settings.DEFAULT_FROM_EMAIL
        recipient_list=[meeting.user.email]
        html_message=render_to_string('meet/email_backend.html',context)
        plain_message='New Meeting Received!'

        try:
          send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=recipient_list,
            html_message=html_message
          )
        except Exception as e:
            return JsonResponse({'exeption':str(e)})
        return JsonResponse({'status': 'success'})

    
    




# TASK MANAGER SECTION
from .models import Docs
from .forms import DocsForm
from django.contrib import messages
from django.shortcuts import get_object_or_404




def stuff(request):
    if request.method == 'POST':
        form = DocsForm(request.POST,request.FILES)
        if form.is_valid():
            stuff=form.save(commit=False)
            stuff.user=request.user
            try:
              stuff.save()
              messages.success(request,'stuff saved!')
              return redirect('stuff')
            except Exception as e:
                return JsonResponse({'exception':str(e)})
    else:
        form = DocsForm() 
    docs=Docs.objects.filter(user=request.user)             
    return render(request,'task/stuff.html',{"form":form,'docs':docs})


def detail_stuff_view(request,pk):
    stuff=get_object_or_404(Docs, pk=pk)
    return render(request,'task/detail_tuff.html',{'stuff':stuff})

def delete(request,pk):
    stuff=get_object_or_404(Docs,pk=pk)
    stuff.delete()
    messages.success(request,'stuff has been deleted ')
    return redirect('stuff')    


# Automate birthday wishes 

import pyautogui
import schedule
import time
import webbrowser
from .forms import BirthdayForm
from .models import Birthday
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse


class IntroWishView(View):
    template_name='meet/intro_wish.html'

    def get(self, request):
        return render(request,self.template_name)
    



class AutomateBirthdayWishes(View):
    template_name = 'meet/schedule_birthday.html'

    def get(self, request, pk=None):
        form = BirthdayForm()
        birthdays = Birthday.objects.filter(user=request.user)
        return render(request, self.template_name, {
            'form': form,
            'birthdays': birthdays,
            'pk': pk
        })

    def post(self, request):
        form = BirthdayForm(request.POST)
        if form.is_valid():
            birthday = form.save(commit=False)
            birthday.user = request.user

            try:
                birthday.save()
                messages.success(request,f'Birthday has been scheduled for {birthday.name}')
            except Exception as e:
                return JsonResponse({'exception': str(e)}, status=400)
        
        return JsonResponse({'message': 'Birthday has been scheduled successfully'}, status=400)
    
    @staticmethod
    def cancel_birthday(request, pk):
        birthday = get_object_or_404(Birthday, pk=pk)
        try:
            birthday.delete()
            messages.success(request,"birthday wish has been cancelled")
            return redirect('schedule_birthday')
        except Exception as e:
            return JsonResponse({'exception':str(e)}, status=400)



    @staticmethod
    def fetch_birthday_details(request, pk):
        if request.method == "GET":
            try:
                birthday = get_object_or_404(Birthday, pk=pk, user=request.user)

                data = {
                    'name': birthday.name,
                    'phone_number': birthday.phone_number,
                    'birthdate': birthday.birthdate.strftime('%Y-%m-%d'),
                    'message': birthday.message,
                    'scheduled_time': birthday.scheduled_time.strftime('%Y-%m-%d %H:%M')
                }

                return JsonResponse(data)

            except Birthday.DoesNotExist:
                return JsonResponse({'error': 'Birthday not found'}, status=404)

        return JsonResponse({'error': 'Invalid request method'}, status=400)
    

# handle custom user reminders
# from meet.forms import ReminderForm
# from .models import Reminder


# class IntroReminder(View):
#     template_name='meet/intro_reminder.html'

#     def get(self, request):
#         return render(request,self.template_name)
    


# class CustomReminderView(View):
#     template_name='meet/set_reminders.html'

#     def get(self, request):
#         meetings=Meeting.objects.filter(user=request.user)
#         form = ReminderForm(request=request)
#         return render(request,self.template_name, {'form':form, 'meetings':meetings})
    
#     def post(self, request):
#         form = ReminderForm(request.POST, request=request)
#         if form.is_valid():
#             reminder = form.save(commit=False)
#             reminder.user= request.user
#             try:
#               reminder.save()
#               messages.success(request,'Reminder set successfully')
#               return redirect('set_reminders')
#             except Exception as e:
#                 return JsonResponse({'Exception': str(e)}, status=500)
#         else:
#             return render(request, self.template_name,{'form':form})
        
#     @staticmethod
#     def delete_meetings(request):
#         meetings=Meeting.objects.filter(user=request.user)
#         try:
#             meetings.delete()
#             messages.success(request,'meetings has been truncated!')
#             return redirect('set_reminders')
#         except Exception as e:
#             return JsonResponse({'exception':str(e)}, status=400)
            
            
             
                      





