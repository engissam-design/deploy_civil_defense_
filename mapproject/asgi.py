import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mapproject.settings')

import django
django.setup()



import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
import map.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mapproject.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            map.routing.websocket_urlpatterns
        )
    ),
})