from django.urls import path
from .views import *

urlpatterns=[
    path('create-task/',create_task, name='create_task'),
    path('get-tasks/<int:org_id>/',get_tasks, name='get_tasks'),
    path('update-task-status/',update_task_status, name='update_task_status')
]