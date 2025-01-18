from django.urls import path

from . import views

urlpatterns=[
       path('save-subscription/', views.save_subscription, name='save_subscription'),
       path('send_notification/', views.send_push_notification, name='send_notification'),
]