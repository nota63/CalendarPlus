from django.urls import path
from .views import *

urlpatterns=[
    path('automate_scheduling/<int:org_id>/<int:app_id>/',automate_scheduling, name='automate_scheduling'),
    path('schedule-meeting/<int:org_id>/',schedule_meeting,name='schedule_meeting'),
    path('delete_automation/<int:org_id>/<int:automation_id>/<int:app_id>/',delete_automation,name='delete_automation')
]