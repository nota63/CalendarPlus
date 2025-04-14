from django.urls import path 
from .views import *

urlpatterns = [
    path('tasks-in-progress/<int:org_id>/',tasks_in_progress_count, name='tasks_in_progress'),
    path('completed-tasks-summary/<int:org_id>/',completed_tasks_summary, name='completed_taks_summary'),
    path('status-over-time/<int:org_id>/',status_over_time_view, name='status_over_time'),
]