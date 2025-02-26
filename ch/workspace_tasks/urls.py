from django.urls import path
from .views import *

urlpatterns=[
    path('create-task/',create_task, name='create_task')
]