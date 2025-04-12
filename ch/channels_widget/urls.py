from django.urls import path
from .views import *

urlpatterns = [
    path('get-channels-widget/<int:org_id>/',fetch_channels_by_org, name='get_channels_widget'),
    path('get-channel-messages/<int:org_id>/<int:channel_id>/',fetch_channel_messages, name='fetch_channel_messages'),
    path('send-channel-message/',send_message_widget, name='send_channel_message'),

]