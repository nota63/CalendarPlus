from django.urls import path
from .views import *

urlpatterns =[
    path('save-widget/',save_dashboard_widget, name='save_widget'),
]