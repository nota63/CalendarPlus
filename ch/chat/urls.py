from django.urls import path
from .views import *
from . import views

# app_name ='chat'

urlpatterns=[
    path('create_room/', JoinRoomView.as_view(), name='create_room'),
    path('join_chat/<str:room_name>/', join_chat, name='join_chat'),
    path('selector_room/',SelectorView.as_view(), name='selector_room'),

    # invitation handle
    path('invitations/', views.invitation_list, name='invitation_list'),
    path('invitations/accept/<int:invitation_id>/', views.accept_invitation, name='accept_invitation'),
    path('invitations/reject/<int:invitation_id>/', views.reject_invitation, name='reject_invitation'),
]
