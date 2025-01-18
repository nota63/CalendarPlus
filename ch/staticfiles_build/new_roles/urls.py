from django.urls import path
from .views import *

urlpatterns=[
    path('add_user/',AddUserView.as_view(), name='add_user'),
    path('features/',feature_implementation, name='features'),
    path('profile_list/',ProfileListView.as_view(), name='profile_list'),
    path('profile_list/delete/<int:profile_id>/', ProfileListView.delete_profile, name='delete_profile'),
    path('add_to_organization/',AddToOrganizationView.as_view(), name='add_to_organization'),
    path('organization_list/', OrganizationListView.as_view(), name='organization_list'),
    path('organizations/<int:pk>/', OrganizationDetailView.as_view(), name='organization_detail'),
    path('organizations/<int:pk>/add_user/', AddUserToOrganizationView.as_view(), name='add_user_to_organizations'),
    path('user_profile/', UserProfileView.as_view(), name='user_profile')

]
