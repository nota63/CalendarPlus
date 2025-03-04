from django.urls import path
from .views import *

urlpatterns=[
    path('purchase_apps/<int:org_id>/',mini_apps_list,name='purchase_apps'),
    path('install/<int:app_id>/<int:org_id>/',mini_app_detail, name='install'),
    path('install-mini-app/',install_mini_app, name='install_mini_app'),
    path('launch_app/<int:org_id>/<int:app_id>/',launch_app, name='launch_app'),
    path("kanban/taskify-workspace/<int:org_id>/<int:app_id>/", add_task_view_workspace, name="add_task"),
    path("kanban/tasks/<int:org_id>/<int:app_id>/", get_tasks_kanban, name="kanban-tasks"),
    path("kanban/update-task/", update_task_status, name="update-task-status"),
    path("kanban/delete-task/", delete_task, name="delete_task"),
    path("kanban/task-details/<int:task_id>/", task_details, name="task_details"),
    # channels
    path('get-workspace-channels/',get_workspace_channels, name='get_workspace_channels'),
    path('delete-all-messages-channels/',delete_all_messages, name='delete_all_messages_channels'),
    path('export-channels/<int:org_id>/',export_channels, name='export_channels'),
    path("analytics/<int:org_id>/", get_channels_analytics, name="get_channels_analytics"),
    path('set-org-expiry/',set_org_expiry,name='set_org_expiry'),
    path('disable-org-expiry/',disable_org_expiry, name='disable_org_expiry'),
    path('get-user-activities/',get_user_activities, name='get_user_activities')

]
