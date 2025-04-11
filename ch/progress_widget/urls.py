from django.urls import path
from .views import *

urlpatterns=[
    path('user-task-progress-widget/<int:org_id>/',user_task_progress_widget, name='user_task_progress_widget')
]