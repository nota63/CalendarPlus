from django.urls import path
from .views import *


urlpatterns=[

    path('modify-organization/<int:org_id>/',edit_organization, name='modify_organization')

]