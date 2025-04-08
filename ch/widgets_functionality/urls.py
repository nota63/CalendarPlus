
from django.urls import path
from .views import *

urlpatterns= [
    path('user-meetings-json/',user_meetings_json, name='user_meetings_json')
]