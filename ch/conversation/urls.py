from django.urls import path
from .views import *

urlpatterns=[
    path('dm/<int:user_id>/',chat_view, name='dm'),
    path('save_message/',save_message, name='save_message'),
    path('save_file/',save_file, name='save_file')
]