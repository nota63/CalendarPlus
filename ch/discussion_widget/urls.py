from django.urls import path
from .views import *

urlpatterns = [
    path('fetch-chat-users/<int:org_id>/',fetch_chat_users, name='fetch_chat_users'),
    path('handle-chat/',handle_chat, name='handle_chat'),
    path('time-spent-battery-chart/<int:org_id>/',time_spent_battery_chart, name='time_spent_battery_chart'),
    path('time-spent-by-group/<int:org_id>/',time_spent_by_group_view, name='time_spent_by_group'),
    path('tasks-by-assignee/<int:org_id>/',fetch_user_pending_tasks_by_org, name='tasks_by_assignee'),
    path('tasks-assignment-summary/<int:org_id>/',task_assignment_summary, name='task_assignment_summary'),
    path('assigned-not-completed/<int:org_id>/',assigned_not_completed_tasks_view, name='assigned_not_completed'),
]
