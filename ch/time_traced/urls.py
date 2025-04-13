from django.urls import path
from .views import *


urlpatterns = [
    path('get-time-traced-tasks/<int:org_id>/',task_time_tracking_summary, name='get_time_traced_tasks'),
    path('high-priority-tasks/<int:org_id>/',high_priority_tasks_widget, name='high_priority_tasks'),
    path('get-calpoints-balance/<int:org_id>/',get_calpoints_balance_view, name='get_calpoints_balance'),
    path('fetch-calpoints-history/<int:org_id>/',fetch_calpoints_history, name='fetch_calpoints_history'),
    path('embed-google-doc/',embed_google_doc, name='embed_google_doc'),
    path('embed-google-sheet/',embed_google_sheet, name='embed_google_sheet'),
    path('embed-youtube-video/',embed_youtube_video, name='embed_youtube_video'),
]
