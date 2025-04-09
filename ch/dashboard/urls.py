from django.urls import path
from .views import *



urlpatterns =[
    path('save-widget/',save_dashboard_widget, name='save_widget'),
    path('widget-snippet/',widget_snippet_view, name='widget_snippet'),
    path('all-widget-snippets/',all_widgets_snippet_view, name='all_widget_snippets'),
    path('remove-widget-from-user/',remove_user_dashboard_widget, name='remove_widget_from_user')

]