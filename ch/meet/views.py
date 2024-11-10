from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Meeting
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import MeetingForm

# Create your views here.from django.shortcuts import render
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

        # push email notification to user 
        subject=f'You Have New Meeting With {request.user}'
        from_email=settings.DEFAULT_FROM_EMAIL
        recipient_list=[user_email]
        html_message=render_to_string('meet/email_backend.html',context)
        plain_message='New Meeting Received!'

        try:# send the email
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

# view to update email address
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
                # send push notification via email to user about his email has been attached
                # create main things
                from_email=settings.DEFAULT_FROM_EMAIL
                recipients_list=[request.user.email]
                subject='Email Has Been Updated !'
                html_message=render_to_string('meet/email_updated.html')
                plain_message='Your Email Has Been Updated'

                # send the email
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

# success page
def done(request):
    return render(request,'meet/done.html')




# get profile info
def get_profile_info(request):
    print("User data:", request.user)
    me=request.user
    return render(request,'meet/profile_info.html',{'me':me})


# fetch device info
import psutil
import socket

def device_info_view(request):
   # Get system information using psutil
    system_name = socket.gethostname()
    system_info = {
        'system_name':system_name,
        'cpu_usage': psutil.cpu_percent(interval=1),
        'memory_info': psutil.virtual_memory(),
        'disk_usage': psutil.disk_usage('/'),
        'network_info': psutil.net_io_counters(),
        'battery': psutil.sensors_battery()  # Get battery info
    }

    # Check if battery info is available
    if system_info['battery']:
        battery_percent = system_info['battery'].percent
        power_plugged = system_info['battery'].power_plugged
        time_left = system_info['battery'].secsleft if system_info[
                                                           'battery'].secsleft != psutil.POWER_TIME_UNLIMITED else None
    else:
        battery_percent = power_plugged = time_left = None

    # Prepare context to pass to the template
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


# take screenshots

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
        # Define the media directory path for screenshots
        gallery_path = os.path.join(settings.MEDIA_ROOT, 'screenshots')
        os.makedirs(gallery_path, exist_ok=True)

        # Generate a unique filename for the screenshot
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        screenshot_filename = f'screenshot_{timestamp}.png'
        screenshot_path = os.path.join(gallery_path, screenshot_filename)

        # Take the screenshot and save it in the media folder
        screenshot = pyautogui.screenshot()
        screenshot.save(screenshot_path)

        # Relative URL path to be used in the template
        relative_path = f'screenshots/{screenshot_filename}'
        full_url = f"{settings.MEDIA_URL}{relative_path}"

        # Render template and pass the screenshot path
        return render(request, 'meet/screenshot_display.html', {'screenshot_url': full_url})
    
# import q for advanced filter
from django.db.models import Q
from datetime import timedelta

class GetMeetingsView(LoginRequiredMixin, View):
    def get(self, request):
        start = request.GET.get('start')
        end = request.GET.get('end')
        meeting_type = request.GET.get('meeting_type', 'all')

        # Filter meetings based on user and date range
        meetings = Meeting.objects.filter(
            Q(admin=request.user) | Q(user=request.user),
            date__range=[start, end]
        )

        if meeting_type != 'all':
            meetings = meetings.filter(meeting_type=meeting_type)

        # Prepare events data for JSON response
        events = []
        for meeting in meetings:
            event_start = f"{meeting.date}T{meeting.time}"
            # Add one-hour duration for each meeting to ensure visibility
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
                'allDay': False  # Adjust if needed
            })

        return JsonResponse(events, safe=False)
    
    
class GetUsersView(LoginRequiredMixin, View):
    def get(self, request):
        users = User.objects.all()
        user_list = [{'id': user.id, 'username': user.username} for user in users]
        return JsonResponse({'users': user_list})

# all meetings         
def user_meetings(request):
    meetings=Meeting.objects.filter(user=request.user)
    return render(request,'meet/user_meetings.html',{'meetings':meetings}) 



# analytics section
from django.db.models import Count, Avg, Max, Min
from datetime import timedelta
from django.utils import timezone
from .models import Meeting
import json
from django.db.models.functions import ExtractHour
def analytics_view(request):
    user = request.user  # current logged-in user
    today = timezone.now().date()

    # 1. Total Meetings
    total_meetings = Meeting.objects.filter(user=user).count()

    # 2. Meeting Count by Type
    meeting_count_by_type = (
        Meeting.objects.filter(user=user)
        .values('meeting_type')
        .annotate(count=Count('id'))
    )

    # 3. Meetings This Week (count per day)
    week_start = today - timedelta(days=today.weekday())
    meetings_this_week = (
        Meeting.objects.filter(user=user, date__gte=week_start)
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )

    # 4. Peak Meeting Hours using `ExtractHour`
    peak_hours = (
        Meeting.objects.filter(user=user)
        .annotate(hour=ExtractHour('time'))
        .values('hour')
        .annotate(count=Count('id'))
        .order_by('hour')
    )

    # 5. Daily Meetings Count
    daily_meetings = (
        Meeting.objects.filter(user=user, date__gte=today - timedelta(days=30))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )

    # Prepare context with JSON serializable data
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
        # set request.user as an admin while saving an instance
        meeting=serializer.save(admin=self.request.user)
         # Email subject and message
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

        # push email notification to user 
        subject=f'You Have New Meeting With {self.request.user}'
        from_email=settings.DEFAULT_FROM_EMAIL
        recipient_list=[meeting.user.email]
        html_message=render_to_string('meet/email_backend.html',context)
        plain_message='New Meeting Received!'

        try:# send the email
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





