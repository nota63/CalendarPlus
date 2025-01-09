
from django.urls import path, include

from .views import *

urlpatterns = [
    path('create_task/<int:org_id>/<int:group_id>/',create_task, name='create_task'),
    path('task-calendar/<int:org_id>/<int:group_id>/',task_calendar, name='task_calendar'),
    path('add-to-my-day/<int:org_id>/<int:group_id>/<int:task_id>/',add_to_my_day, name='add_to_my_day'),
    path('task_detail/<int:org_id>/<int:group_id>/<int:task_id>/',my_day_task_detail, name='task_detail'),
    path('task/<int:org_id>/<int:group_id>/<int:task_id>/add_comment/',add_comment, name='add_comment'),
    path('task/<int:org_id>/<int:group_id>/<int:task_id>/add_note/', add_task_note, name='add_task_note'),
    path('task/<int:org_id>/<int:group_id>/<int:task_id>/manage_timer/',manage_task_timer, name='manage_task_timer'),
    path('tasks/<int:org_id>/<int:group_id>/<int:task_id>/update_progress/',update_task_progress, name='update_task_progress'),
    path('tasks/<int:org_id>/<int:group_id>/<int:task_id>/activity_logs/', fetch_activity_logs, name='fetch_activity_logs'),
    path('tasks/<int:org_id>/<int:group_id>/<int:task_id>/toggle_status/', toggle_task_status, name='toggle_task_status'),
    path('tasks/<int:org_id>/<int:group_id>/<int:task_id>/update_tags/',update_tags, name='update_tags'),
    path('tasks/<int:org_id>/<int:group_id>/<int:task_id>/save_time/',save_time, name='save_time'),
  
]


