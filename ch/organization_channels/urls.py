
from django.urls import path 
from .views import *

urlpatterns = [
    path('organization/<int:org_id>/channel/',create_channel, name='create_channel'),
    path('statistics/<int:org_id>/', channel_statistics, name='channel_statistics'),
    path('organization/<int:org_id>/channels/',ChannelListView.as_view(), name='channels_list'),
    path('channel/<int:channel_id>/chat/',channel_chat, name='channel_chat'),
    path('get_organization_members/<int:organization_id>/', get_organization_members, name='get_organization_members'),
    path('channels/get_members/<int:org_id>/<int:channel_id>/',get_channel_members, name='get_channel_members'),
    path('channels/fetch_activity_logs/<int:channel_id>/<int:org_id>/', fetch_activity_logs, name='fetch_activity_logs'),
    path('channels/search/<int:org_id>/<int:channel_id>/',search_messages_links, name='search_messages_links'),
    path('channels/channel_details/<int:org_id>/<int:channel_id>/',channel_details, name='channel_details'),
    path('export_data/<int:org_id>/<int:channel_id>/', export_data, name='export_data'),
    path('channel/statistics/<int:org_id>/<int:channel_id>/', channel_statistics, name='channel_statistics'),
    path('filter_messages/<int:org_id>/<int:channel_id>/',filter_messages, name='filter_messages'),


]