from django.urls import path
from .views import *

urlpatterns=[
    path('dm/<int:user_id>/<int:org_id>/',chat_view, name='dm'),
    path('save_message/<int:org_id>/',save_message, name='save_message'),
    path('save_file/<int:org_id>/',save_file, name='save_file'),
    path("save-code/<int:org_id>/", save_code_snippet, name="save_code_snippet"),
    path("edit-message/<int:message_id>/<int:org_id>/", edit_message, name="edit_message"),
    path('set-recurrence/<int:message_id>/<int:org_id>/',set_recurrence, name='set_recurrence'),
    path('delete_text/<int:message_id>/<int:org_id>/',delete_message, name='delete_text'),
]