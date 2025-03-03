from django.urls import path
from .views import *

urlpatterns=[
    path('purchase_apps/<int:org_id>/',mini_apps_list,name='purchase_apps'),
    path('install/<int:app_id>/<int:org_id>/',mini_app_detail, name='install'),
    path('install-mini-app/',install_mini_app, name='install_mini_app'),
    path('launch_app/<int:org_id>/<int:app_id>/',launch_app, name='launch_app')
]