from django.urls import path
from .consumers import ChatConsumerNew

websocket_urlpatterns = [
    path('ws/channel/<int:channel_id>/', ChatConsumerNew.as_asgi()),  
]
