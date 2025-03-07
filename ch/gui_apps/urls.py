from django.urls import path
from .views import *

urlpatterns=[
    path('automate_scheduling/<int:org_id>/<int:app_id>/',automate_scheduling, name='automate_scheduling'),
]