from django.urls import path
from .views import *

urlpatterns=[
    path('dm/<int:user_id>/',chat_view, name='dm')
]