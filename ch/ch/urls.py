"""
URL configuration for ch project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from .import views
from django.conf import settings
from django.conf.urls.static import static
from calendar_plus.views import *


urlpatterns = [
    path('admin/', admin.site.urls),
    path('latest_pending_reward/',views.latest_pending_reward, name='latest_pending_reward'),
    # path('',LandingPageView.as_view(), name='landing_page'),
    path('',views.home, name='home'),
    path('meet/', include('meet.urls')),
    path('accounts/', include('accounts.urls')),
    path('chat/', include('chat.urls')),
    path('notify/', include('notify.urls')),
    path('ai/', include('ai.urls')),
    path('new_roles/', include('new_roles.urls')),
    path('calendar/', include('calendar_plus.urls')),
    path('test/',views.test_base, name='test'),
    path('contacts/',include('contacts.urls')),
    path('security/', include('security.urls')),
    path('groups/', include('groups.urls')),
    path('tasks/',include('group_tasks.urls')),
    path('channels/',include('organization_channels.urls')),
    path('profiles/',include('profiles.urls')),
    path('organizations/',include('organizations.urls')),
    path('oauth/',include('outh.urls')),
    path('dm/',include('conversation.urls')),
    path('taskify/',include('workspace_tasks.urls')),
    path('apps/',include('app_marketplace.urls')),
    path('gui_apps/',include('gui_apps.urls')),
    path('cal_ai/',include('cal_ai.urls')),
    path('subscription/',include('subscription.urls')),
    # ui components
    path('index/', views.styles, name= 'index'),
    path('weather/',views.weather, name='weather'),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    # middlewares
    path('update-email/',views.update_email, name='update_email'),
    path('guide/', views.GuideView.as_view(), name='guide_page'),
    path('org_guide/',views.OrgGuideView.as_view(), name='org_guide')

  

  

]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

