from django.urls import path
from .views import *

urlpatterns = [
    path('user-bookmarks/<int:org_id>/', UserBookmarksView.as_view(), name='user-bookmarks'),
    path('add-bookmark/<int:org_id>/',add_bookmark, name='add_bookmark'),
  
]
