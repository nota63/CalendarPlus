from django.urls import path
from .views import *

urlpatterns = [
    path('user-events-calendar/<int:org_id>/',user_events_for_calendar, name='user_events_calendar'),
]