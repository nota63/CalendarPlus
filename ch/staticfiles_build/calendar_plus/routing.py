from django.urls import re_path
from .consumers import MeetingNotesConsumer

websocket_urlpatterns = [
    re_path(r'ws/meeting_notes/(?P<org_id>\d+)/(?P<meeting_id>\d+)/$', MeetingNotesConsumer.as_asgi()),
]
