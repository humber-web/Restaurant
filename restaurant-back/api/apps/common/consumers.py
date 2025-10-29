"""
WebSocket consumers for real-time updates.
"""
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OrderConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time order updates.
    Handles order creation, updates, and status changes.
    """
    async def connect(self):
        """Accept the connection and add to 'orders' group."""
        await self.channel_layer.group_add("orders", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """Remove from 'orders' group on disconnect."""
        await self.channel_layer.group_discard("orders", self.channel_name)

    async def receive(self, text_data):
        """
        Receive message from WebSocket and broadcast to group.
        
        Expected format:
        {
            "message": "Order created",
            "order": {...order data...}
        }
        """
        try:
            # Parse the incoming JSON data
            data = json.loads(text_data)
            logger.info(f"Received message: {data}")

            # Access the 'message' and 'order' from the parsed JSON
            message = data['message']
            order = data['order']

            # Broadcast the message to all connected clients in the "orders" group
            await self.channel_layer.group_send(
                "orders",
                {
                    "type": "send_order_update",
                    "message": message,
                    "order": order
                }
            )
        except Exception as e:
            logger.error(f"Error: {e}")
            await self.send(text_data=json.dumps({
                'error': 'Invalid message'
            }))

    async def send_order_update(self, event):
        """
        Handler for 'send_order_update' events from the group.
        Sends the order update to the WebSocket client.
        """
        message = event['message']
        order = event['order']
        
        logger.info(f"Sending message: {json.dumps({'message': message, 'order': order})}")

        # Send the message to WebSocket clients
        await self.send(text_data=json.dumps({
            'message': message,
            'order': order
        }))
