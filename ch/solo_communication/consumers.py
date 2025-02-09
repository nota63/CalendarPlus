import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from .models import Message
from asgiref.sync import sync_to_async
from django.db.utils import IntegrityError

# Enable logging for debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handle WebSocket connection."""
        self.user = self.scope["user"]

        if self.user.is_anonymous:
            await self.close()
            return

        self.other_username = self.scope["url_route"]["kwargs"]["username"]
        
        try:
            self.other_user = await sync_to_async(User.objects.get, thread_sensitive=True)(username=self.other_username)
        except User.DoesNotExist:
            await self.close()
            return

        # Generate room name for both users
        self.room_name = f"chat_{min(self.user.id, self.other_user.id)}_{max(self.user.id, self.other_user.id)}"
        self.room_group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Fetch last 20 messages from DB
        last_messages = await sync_to_async(
            lambda: list(
                Message.objects.filter(
                    sender__in=[self.user, self.other_user], 
                    receiver__in=[self.user, self.other_user]
                ).order_by("-timestamp")[:20]
            ),
            thread_sensitive=True
        )()

        # Send previous messages to the frontend
        for msg in reversed(last_messages):
            await self.send(text_data=json.dumps({
                "message": msg.message,
                "sender": msg.sender.username,
            }))

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """Handle messages received from WebSocket."""
        try:
            data = json.loads(text_data)
            message = data.get("message", "").strip()

            if not message:
                return

            # Ensure sender and receiver are correct
            message_obj = await sync_to_async(Message.objects.create, thread_sensitive=True)(
                sender=self.user, receiver=self.other_user, message=message
            )

            # Send message to WebSocket group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message_obj.message,
                    "sender": self.user.username,
                },
            )

        except json.JSONDecodeError:
            logger.error("JSON decode error in WebSocket message.")
        except IntegrityError:
            logger.error("Database IntegrityError while saving message.")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")

    async def chat_message(self, event):
        """Send chat messages to WebSocket clients."""
        await self.send(text_data=json.dumps(event))
