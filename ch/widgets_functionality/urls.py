
from django.urls import path
from .views import *

urlpatterns= [
    path('user-meetings-json/',user_meetings_json, name='user_meetings_json'),
    # 2) tasks widget
    path('get-user-groups-json/',get_user_groups_json, name='get_user_groups_json')
]