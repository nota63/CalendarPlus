
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
    path('tasks/<int:org_id>/<int:group_id>/<int:task_id>/create_problem/',create_problem, name='create_problem'),
    path('tasks/<int:org_id>/<int:group_id>/<int:task_id>/resolve_problem/<int:problem_id>/',resolve_problem, name='resolve_problem'),
    path('tasks/<int:org_id>/<int:group_id>/<int:task_id>/<int:note_id>/delete_note/',delete_task_note, name='delete_note'),
    path('tasks/<int:org_id>/<int:group_id>/<int:task_id>/<int:note_id>/edit_note/',edit_task_note, name='edit_note'),
    path('tasks/<int:org_id>/<int:group_id>/<int:task_id>/<int:comment_id>/edit_comment/',edit_task_comment, name='edit_comment'),
    path('tasks/<int:org_id>/<int:group_id>/<int:task_id>/<int:comment_id>/delete_comment/',delete_task_comment, name='delete_comment'),
    # Team leader features 
    path('tasks/assigned-users/<int:org_id>/<int:group_id>/', AssignedUsersListView.as_view(), name='assigned_users_list'),
    path('tasks/users-task/<int:org_id>/<int:group_id>/<int:user_id>/', user_tasks_view, name='users_tasks'),
    path('tasks/task-detail/<int:org_id>/<int:group_id>/<int:task_id>/<int:user_id>/',TaskDetailView.as_view(), name='task_details'),
    path('tasks/<int:org_id>/<int:group_id>/<int:task_id>/add_comment/',add_task_comment, name='add_comment'),
    # extend tasks app
    path('cancel-task/<int:org_id>/<int:group_id>/<int:task_id>/',cancel_task, name='cancel_task'),
    path('create-subtask/<int:org_id>/<int:group_id>/<int:task_id>/',create_subtask,name='create_subtask'),
    path("subtasks/<int:org_id>/<int:group_id>/<int:task_id>/", fetch_subtasks, name="fetch_subtasks"),
    path("subtasks/update/<int:org_id>/<int:group_id>/<int:task_id>/<int:subtask_id>/", update_subtask, name="update_subtask"),
    path("subtasks/delete/<int:org_id>/<int:group_id>/<int:task_id>/<int:subtask_id>/", delete_subtask, name="delete_subtask"),
    path('export-task-data/<int:org_id>/<int:group_id>/<int:task_id>/',export_task_data,name='export_task_data'),
    path('attach-task-file/<int:org_id>/<int:group_id>/<int:task_id>/',attach_task_file,name='attach_task_file'),
    path('fetch-recent-tabs/',fetch_recent_tabs,name='fetch_recent_tabs'),
    path('clear-recent-tabs/',clear_recent_tabs,name='clear_recent_tabs'),
    path("fetch-task-attachments/<int:org_id>/<int:group_id>/<int:task_id>/", fetch_task_attachments, name="fetch_task_attachments"),
    path("delete-task-attachment/<int:org_id>/<int:group_id>/<int:task_id>/<int:attachment_id>/", delete_task_attachment, name="delete_task_attachment"),
    path('retry-task-attachment/<int:org_id>/<int:group_id>/<int:task_id>/<int:attachment_id>/', retry_task_attachment, name="retry_task_attachment"),
    path('send-task-query/<int:org_id>/<int:group_id>/<int:task_id>/',send_task_email, name='send_task_query'),
    path('get-available-slots/',get_available_slots, name='get_available_slots'),
    path('schedule-the-meeting/',schedule_meeting, name='schedule_the_meeting'),
    path('get-existing-meetings/',get_existing_meetings, name='get_existing_meetings'),
    path('fetch-task-meetings/',fetch_task_meetings,name='fetch_task_meetings'),
    path('update-meeting-status/',update_meeting_status, name='update_meeting_status'),
    path('fetch-task-messages/<int:org_id>/<int:group_id>/<int:task_id>/',fetch_task_messages, name='fetch_task_messages'),
    path('send-task-message/',send_task_message, name='send_task_message'),
  
  
  
  
  
  
  
  
  
  
  
  
]


