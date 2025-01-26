"""
ASGI config for face_reconition project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import tictactoeapp.routing  # Replace `your_app` with the name of your app

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tictactoe.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            tictactoeapp.routing.websocket_urlpatterns
        )
    ),
})

