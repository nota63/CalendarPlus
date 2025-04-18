from django.urls import path
from .views import *

urlpatterns = [
    path('create-workspace/',create_organization_and_invite, name='create_workspace'),
]