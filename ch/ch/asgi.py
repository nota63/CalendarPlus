"""
ASGI config for ch project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/

"""
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
import chat.routing
import calendar_plus.routing
import organization_channels.routing
import conversation.routing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ch.settings')


django_asgi_app = get_asgi_application()




application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket':AuthMiddlewareStack(URLRouter(
        chat.routing.ws_urlpatterns + 
        calendar_plus.routing.websocket_urlpatterns +
        organization_channels.routing.websocket_urlpatterns+
        conversation.routing.websocket_urlpatterns
        
          
        
    ))
})


