from django.urls import path
from .views import *

urlpatterns=[
    path('user-task-progress-widget/<int:org_id>/',user_task_progress_widget, name='user_task_progress_widget'),
    path('get-task-progress-details/<int:org_id>/<int:task_id>/',get_task_progress_details, name='get_task_progress_details')
]