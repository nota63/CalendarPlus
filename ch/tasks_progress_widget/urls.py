from django.urls import path
from .views import *

urlpatterns =[
    path('list-groups/<int:org_id>/',group_leader_info_view,name='list_groups'),
    path('group-analytics-widget/<int:org_id>/<int:group_id>/',group_task_analytics_view, name='group_analytics_widget'),
    path('group-task-completion-velocity/<int:org_id>/',group_task_completion_velocity, name='group_task_completion_velocity'),
    path('get-assignable-groups/<int:org_id>/',get_assignable_groups_ajax, name='get_assignable_groups'),
    path('assign-task-widget/<int:org_id>/<int:group_id>/',assign_task_to_group_member, name='assign_task_widget'),
    path('get-user-by-email/<int:org_id>/',get_user_by_email, name='get_user_by_email'),
]
