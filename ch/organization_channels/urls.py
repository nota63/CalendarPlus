
from django.urls import path 
from .views import *

urlpatterns = [
    path('organization/<int:org_id>/channel/',create_channel, name='create_channel')


]