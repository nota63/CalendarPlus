from django.urls import path
from .views import *

urlpatterns = [
    path('user-bookmarks/<int:org_id>/', UserBookmarksView.as_view(), name='user-bookmarks'),
    path('add-bookmark/<int:org_id>/',add_bookmark, name='add_bookmark'),
    path('delete-bookmark/<int:org_id>/<int:bookmark_id>/',delete_bookmark, name='delete_bookmark'),
    path('user-resources/<int:org_id>/',user_resources_view, name='user_resources'),
    path('fetch-recent-activity-methods/<int:org_id>/',fetch_recent_activity_methods, name='fetch_recent_activity_methods'),
    path('recent-activity-detail/<int:org_id>/<int:activity_id>/',fetch_recent_activity_detail, name='recent_activity_detail')
  
]
