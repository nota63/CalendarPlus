from django.urls import path
from .views import *


urlpatterns = [
    path('manage_members/<int:org_id>/',manage_members, name='manage_members'),
    path("organization/<int:org_id>/change_role/<int:member_id>/", change_role, name="change_role"),
    path('remove_member/<int:org_id>/<int:member_id>/', remove_member, name='remove_member'),
    path('send_invitation/<org_id>/',send_email_invitation, name='send_invitation'),
    path('invitations/status/<int:org_id>/', fetch_invitations_status, name='fetch_invitations_status'),
   
]