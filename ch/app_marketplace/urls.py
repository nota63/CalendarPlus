from django.urls import path
from .views import *

urlpatterns=[
    path('purchase_apps/<int:org_id>/',mini_apps_list,name='purchase_apps')
]