
from django.urls import path
from .views import *

urlpatterns= [
    path('user-meetings-json/',user_meetings_json, name='user_meetings_json'),
    # 2) tasks widget
    path('get-user-groups-json/',get_user_groups_json, name='get_user_groups_json'),
    path('get-user-tasks-by-group/',get_user_tasks_by_group, name='get_user_tasks_by_groups'),
    path('group-tasks-calendar-view/',group_tasks_calendar_view, name='group_tasks_calendar_view')
]