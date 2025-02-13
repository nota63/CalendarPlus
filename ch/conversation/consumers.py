import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from django.db.models import Q
from asgiref.sync import sync_to_async
from .models import Conversation, Message

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = self.room_name  # Use the same room name everywhere

        # Join the chat room
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the chat room
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_text = data["message"]
        sender_id = self.user.id

        # Extract user IDs from the room name
        user1_id, user2_id = map(int, self.room_name.split("_")[1:])  # Extract IDs from chat_x_y
        receiver_id = user2_id if sender_id == user1_id else user1_id

        # Save the message to the database
        conversation = await sync_to_async(self.get_or_create_conversation)(user1_id, user2_id)
        message = await sync_to_async(self.save_message)(conversation, sender_id, message_text)

        # Send message to the group
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
        """Send the received message to the WebSocket."""
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender_id": event["sender_id"],
            "timestamp": event["timestamp"],
        }))

    def get_or_create_conversation(self, user1_id, user2_id):
        """Get or create a conversation between two users."""
        user1 = User.objects.get(id=user1_id)
        user2 = User.objects.get(id=user2_id)
        conversation, created = Conversation.objects.get_or_create(
            user1=min(user1, user2, key=lambda x: x.id),
            user2=max(user1, user2, key=lambda x: x.id)
        )
        return conversation

    def save_message(self, conversation, sender_id, text):
        """Save a new message to the database."""
        sender = User.objects.get(id=sender_id)
        message = Message.objects.create(conversation=conversation, sender=sender, text=text)
        return message

