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
    path('get-user-activities/',get_user_activities, name='get_user_activities'),
    # dashboard
    path('get-dashboard-data/<int:org_id>/',get_dashboard_data, name='get_dashboard_data'),
    # Meeting Notes
    path('show-user-meetings/<int:org_id>/<int:user_id>/',fetch_user_meetings, name='show-user-meetings'),
    path('add-meeting-note/',add_meeting_note, name='add_meeting_note'),
    path("get-meeting-notes/<int:meeting_id>/", get_meeting_notes, name="get_meeting_notes"),
    path("delete-meeting-note/<int:note_id>/", delete_meeting_note, name="delete_meeting_note"),
    # bookmarks
    path("bookmarks/fetch/<int:org_id>/", fetch_bookmarks, name="fetch_bookmarks"),
    path("bookmarks/delete/<int:org_id>/<int:bookmark_id>/", delete_bookmark, name="delete_bookmark"),
    path("bookmarks/add/<int:org_id>/", add_bookmark, name="add_bookmark"),
    # share-mania
    path('share_mania_app/<int:org_id>/<int:app_id>/',share_mania,name='share_mania_app'),
    path('upload-file/<int:org_id>/',upload_file,name='upload_file'),
    path('fetch-members-workspace/<int:org_id>/',fetch_members_and_send_email,name='fetch_members_workspace'),
    path("share-file/<uuid:unique_link>/", file_details_view, name="file_details"),
    path("download-file/<uuid:unique_link>/", download_file, name="download_file"),
    path('download-file-preview/<uuid:unique_link>/',file_details_view,name='download_file_preview'),
    path('download-file/<uuid:uinique_link>/',download_file,name='download_file'),
    path('fetch-file-details/<uuid:unique_link>/',fetch_file_details,name='fetch_file_details'),
    path('delete_file/<int:org_id>/<int:file_id>/<int:app_id>/',delete_file_upload, name='delete_file'),
    # ajax set-up to preview and uninstall the apps
    path('fetch-installed-apps/<int:org_id>/',fetch_installed_apps, name='fetch_installed_apps'),
    path("uninstall/<int:org_id>/<int:app_id>/", uninstall_app, name="uninstall_app"),
    path("miniapp-details/<int:org_id>/<int:app_id>/", fetch_app_details, name="fetch_app_details"),
    

]
