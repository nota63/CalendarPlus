from django.urls import path  
from .consumers import ChatConsumer

websocket_urlpatterns = [
    path("ws/chat/<str:room_name>/", ChatConsumer.as_asgi()),  # Use room_name instead of user_id
]
