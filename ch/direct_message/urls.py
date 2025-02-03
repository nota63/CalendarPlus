from django.urls import path
from .import views
from .views import *


urlpatterns=[
  path('direct_messages/<int:organization_id>/',views.organization_members, name='direct_messages'),
  path('start-chat/<int:org_id>/<int:user_id>/', views.start_chat, name='start_chat'),
  path('chat-room/<int:conversation_id>/', views.chat_room, name='chat_room'),

]