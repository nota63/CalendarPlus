from django.urls import path
from .views import *

urlpatterns = [
    path('get-channels-widget/<int:org_id>/',fetch_channels_by_org, name='get_channels_widget'),
]