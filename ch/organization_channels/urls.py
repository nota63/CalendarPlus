
from django.urls import path 
from .views import *

urlpatterns = [
    path('organization/<int:org_id>/channel/',create_channel, name='create_channel'),
    path('statistics/<int:org_id>/', channel_statistics, name='channel_statistics'),
    path('organization/<int:org_id>/channels/',ChannelListView.as_view(), name='channels_list'),
    path('channel/<int:channel_id>/chat/',channel_chat, name='channel_chat'),
    path('get_organization_members/<int:organization_id>/', get_organization_members, name='get_organization_members'),
    path('channels/get_members/<int:org_id>/<int:channel_id>/',get_channel_members, name='get_channel_members'),


]