from django.urls import path
from .views import *

urlpatterns =[
    path('list-groups/<int:org_id>/',group_leader_info_view,name='list_groups'),
    path('group-analytics-widget/<int:org_id>/<int:group_id>/',group_task_analytics_view, name='group_analytics_widget'),
]