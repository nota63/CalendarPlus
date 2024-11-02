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
    path('delete/<int:pk>/',delete, name='delete')
]
