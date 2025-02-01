from django.urls import path
from .views import *


urlpatterns=[

    path('modify-organization/<int:org_id>/',edit_organization, name='modify_organization'),
    path('workspace-invitations/<int:org_id>/',organization_invitations, name='workspace_invitations'),
    path('customize_workspace/<int:org_id>/',customize_workspace, name='customize_workspace'),
    path('workspace-icon/<int:org_id>/',update_workspace_icon, name='workspace_icon')

]