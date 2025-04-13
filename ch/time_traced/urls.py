from django.urls import path
from .views import *


urlpatterns = [
    path('get-time-traced-tasks/<int:org_id>/',task_time_tracking_summary, name='get_time_traced_tasks'),
    path('high-priority-tasks/<int:org_id>/',high_priority_tasks_widget, name='high_priority_tasks'),
    path('get-calpoints-balance/<int:org_id>/',get_calpoints_balance_view, name='get_calpoints_balance'),
]
