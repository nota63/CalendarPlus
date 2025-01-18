from django.urls import path
from chat import consumers


ws_urlpatterns=[
    path('ws/chat/<str:room_name>/',consumers.ChatConsumer.as_asgi()),  
]