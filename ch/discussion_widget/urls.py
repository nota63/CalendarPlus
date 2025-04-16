from django.urls import path
from .views import *

urlpatterns = [
    path('fetch-chat-users/<int:org_id>/',fetch_chat_users, name='fetch_chat_users'),
    path('handle-chat/',handle_chat, name='handle_chat'),
    path('time-spent-battery-chart/<int:org_id>/',time_spent_battery_chart, name='time_spent_battery_chart'),
    path('time-spent-by-group/<int:org_id>/',time_spent_by_group_view, name='time_spent_by_group'),
]