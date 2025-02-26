from django.urls import path
from .views import *

urlpatterns=[
    path('create-task/',create_task, name='create_task'),
    path('get-tasks/<int:org_id>/',organization_tasks, name='get_tasks'),
    path("update_task_status/<int:task_id>/", update_task_status, name="update_task_status"),

]