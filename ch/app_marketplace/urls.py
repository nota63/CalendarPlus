from django.urls import path
from .views import *

urlpatterns=[
    path('purchase_apps/<int:org_id>/',mini_apps_list,name='purchase_apps'),
    path('install/<int:app_id>/<int:org_id>/',mini_app_detail, name='install')
]