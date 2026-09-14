import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import map.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mapproject.settings')

# تحميل Django ASGI أولاً
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            map.routing.websocket_urlpatterns
        )
    ),
})