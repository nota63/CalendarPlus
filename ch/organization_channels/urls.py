
from django.urls import path 
from .views import *

urlpatterns = [
    path('organization/<int:org_id>/channel/',create_channel, name='create_channel'),
    path('statistics/<int:org_id>/', channel_statistics, name='channel_statistics'),
    path('organization/<int:org_id>/channels/',ChannelListView.as_view(), name='channels_list'),
    path('channel/<int:channel_id>/chat/',channel_chat, name='channel_chat'),


]