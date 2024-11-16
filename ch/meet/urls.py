from django.urls import path, include
from .views import RenderCalendarView, CreateMeetingView, GetMeetingsView, GetUsersView, user_meetings, update_email, done, get_profile_info
from .views import MeetingSet
from rest_framework.routers import DefaultRouter
from .views import *
router=DefaultRouter()

router.register(r'meetings', MeetingSet, basename='meeting')


urlpatterns = [
    path('render-calendar/', RenderCalendarView.as_view(), name='render_calendar'),
    path('create-meeting/', CreateMeetingView.as_view(), name='create_meeting'),
    path('get-meetings/', GetMeetingsView.as_view(), name='get_meetings'),
    path('get-users/', GetUsersView.as_view(), name='get_users'),
    path('user_meetings/',user_meetings, name='user_meetings'),
    path('api/', include(router.urls)),
    path('update_email/',update_email, name='update_email'),
    path('done/', done, name='done'),
    path('profile_info/',get_profile_info, name='profile_info'),
    path('device_info/',device_info_view, name='device_info'),
    path('take_shots/', TakeScreenshotView.as_view(), name='take_shots'),
    path('analytics/',analytics_view, name='analytics'),
    path('stuff/', stuff, name='stuff'),
    path('detail/<int:pk>/', detail_stuff_view, name='detail'),
    path('delete/<int:pk>/',delete, name='delete'),
    path('count/',MeetingCountView.as_view(), name='count'),
    path('intro/', IntroAnalysisView.as_view(), name='intro'),
    path('schedule_birthday/',AutomateBirthdayWishes.as_view(), name='schedule_birthday'),
    path('schedule_birthday/fetch/<int:pk>/', AutomateBirthdayWishes.fetch_birthday_details,   name='fetch_birthday_details'), 
    path('schedule_birthday/cancel/<int:pk>/',   AutomateBirthdayWishes.cancel_birthday, name='cancel_birthday'),
    path('intro_wish/', IntroWishView.as_view(),  name='intro_wish'),
    path('set_reminders/', CustomReminderView.as_view(), name='set_reminders'),
    path('set_reminders/delete/',CustomReminderView.delete_meetings, name='delete_meetings'),
    path('intro_reminder/', IntroReminder.as_view(), name='intro_reminder')

]

