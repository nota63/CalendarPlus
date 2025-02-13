import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from django.contrib.auth import get_user_model
from conversation.models import Conversation, Message

User = get_user_model()
logger = logging.getLogger("channels")

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = self.room_name

        logger.info(f"[CONNECT] User {self.user.id} connected to {self.room_group_name}")

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        logger.info(f"[DISCONNECT] User {self.user.id} left {self.room_group_name}")
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_text = data.get("message", "").strip()
        sender_id = self.user.id

        if not message_text:
            logger.warning("[WARNING] Received empty message, ignoring...")
            return

        logger.debug(f"[RECEIVE] Message from {sender_id}: {message_text}")

        # Extract user IDs from room name
        try:
            user1_id, user2_id = map(int, self.room_name.split("_")[1:])
            receiver_id = user2_id if sender_id == user1_id else user1_id
        except ValueError:
            logger.error(f"[ERROR] Invalid room name format: {self.room_name}")
            return

        logger.info(f"[INFO] Sender: {sender_id}, Receiver: {receiver_id}")

        # Save message in DB
        conversation = await self.get_or_create_conversation(user1_id, user2_id)
        message = await self.save_message(conversation, sender_id, message_text)

        # Send message to WebSocket group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message.text,
                "sender_id": sender_id,
                "timestamp": str(message.timestamp),
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender_id": event["sender_id"],
            "timestamp": event["timestamp"],
        }))
        logger.info(f"[MESSAGE SENT] {event['message']} from {event['sender_id']}")

    @database_sync_to_async
    def get_or_create_conversation(self, user1_id, user2_id):
        """Ensure conversation exists between two users."""
        user1 = User.objects.get(id=user1_id)
        user2 = User.objects.get(id=user2_id)
        conversation, created = Conversation.objects.get_or_create(
            user1=min(user1, user2, key=lambda x: x.id),
            user2=max(user1, user2, key=lambda x: x.id)
        )
        logger.info(f"[CONVERSATION] {'Created' if created else 'Retrieved'} for {user1_id} & {user2_id}")
        return conversation

    @database_sync_to_async
    def save_message(self, conversation, sender_id, text):
        """Store message in the database."""
        sender = User.objects.get(id=sender_id)
        message = Message.objects.create(
            conversation=conversation,
            sender=sender,
            text=text,
            is_read=True,
        )
        logger.info(f"[MESSAGE SAVED] {text} from {sender_id}")
        return message
