from django.urls import path,re_path
from .consumers import ChatConsumer

websocket_urlpatterns = [
    path("ws/chat/<str:room_name>/", ChatConsumer.as_asgi()),  # Use room_name instead of user_id

    re_path(r"ws/status/$", ChatConsumer.as_asgi()),  # Broadcast status updates
]
