from django.urls import path
from .views import *

urlpatterns =[
    path('save-widget/', SaveDashboardWidgetView.as_view(), name='save_dashboard_widget'),
]