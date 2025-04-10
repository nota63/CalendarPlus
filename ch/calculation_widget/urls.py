from django.urls import path

from .views import *

urlpatterns= [
    path('get-calculation/<int:org_id>/',get_sum_calculation, name='get_calculation')
]