from django.urls import path
from .views import *


urlpatterns=[
    path('direct_message/<int:org_id>/',organization_members, name='direct_message')
]

