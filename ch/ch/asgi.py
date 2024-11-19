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
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path
import chat.routing


# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ch.settings')

# Initialize the Django application for ASGI
django_asgi_app = get_asgi_application()

# Define your WebSocket URL patterns (if any)
websocket_urlpatterns = [
    # Example WebSocket URL pattern:
    # path('ws/some_path/', SomeConsumer.as_asgi()),
]

# Set up the ASGI application with Channels
application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket':AuthMiddlewareStack(URLRouter(
        chat.routing.ws_urlpatterns
    ))
})
