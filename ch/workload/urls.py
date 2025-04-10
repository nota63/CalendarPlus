from django.urls import path
from .views import *

urlpatterns = [
    path('meeting-workload-widget/<int:org_id>/',meeting_analytics_view_widget, name='meeting-workload-widget'),

]