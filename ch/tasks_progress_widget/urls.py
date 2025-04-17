from django.urls import path
from .views import *

urlpatterns =[
    path('group-analytics-widget/<int:org_id>/',group_task_analytics_view, name='group_analytics_widget'),
]