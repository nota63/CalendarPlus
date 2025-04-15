from django.urls import path
from .views import *

urlpatterns = [
    path('fetch-chat-users/<int:org_id>/',fetch_chat_users, name='fetch_chat_users'),
    path('handle-chat/',handle_chat, name='handle_chat'),
]