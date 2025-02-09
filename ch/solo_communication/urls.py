from django.urls import path
from .views import home, chat_view

urlpatterns = [
    path("chat_home/", home, name="home"),
    path("chat/<str:username>/", chat_view, name="chat"),
]
