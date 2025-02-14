from django.urls import path
from .views import *

urlpatterns=[
    path('dm/<int:user_id>/',chat_view, name='dm'),
    path('save_message/',save_message, name='save_message'),
    path('save_file/',save_file, name='save_file'),
    path("save-code/", save_code_snippet, name="save_code_snippet"),
    path("edit-message/<int:message_id>/", edit_message, name="edit_message"),
    path('set-recurrence/<int:message_id>/',set_recurrence, name='set_recurrence')
]