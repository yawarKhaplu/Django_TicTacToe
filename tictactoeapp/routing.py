from django.urls import re_path, path
from .consumers import MyConsumer

websocket_urlpatterns = [
    # re_path(r'ws/somepath/$', MyConsumer.as_asgi()),
    path('ws/game/', MyConsumer.as_asgi()),  # Ensure this path matches
    path('wss/game/', MyConsumer.as_asgi()),  # Ensure this path matches
]