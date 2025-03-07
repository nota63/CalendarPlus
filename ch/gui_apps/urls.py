from django.urls import path
from .views import *

urlpatterns=[
    path('automate_scheduling/<int:org_id>/<int:app_id>/',automate_scheduling, name='automate_scheduling'),
    path('schedule-meeting/<int:org_id>/',schedule_meeting,name='schedule_meeting')
]