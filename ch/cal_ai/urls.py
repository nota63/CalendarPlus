from django.urls import path
from .views import *

urlpatterns=[
    path('cal-ai/<int:org_id>/<int:group_id>/<int:task_id>/',calai_task_analysis, name='cal_ai')
]
