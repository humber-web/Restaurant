from django.urls import path
from apps.common.consumers import OrderConsumer

websocket_urlpatterns = [
    path('ws/orders/', OrderConsumer.as_asgi()),
]
