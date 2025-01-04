
from django.urls import path
from .views import *


urlpatterns = [
    path('security/<int:org_id>/',security_view, name='security'),
    path('confirm_security/<int:org_id>/<str:email>/',delete_user_actions, name='confirm_security'),
    path('managed_workflows/<int:org_id>/', ManagedWorkflows.as_view(), name='managed_workflows')
]






