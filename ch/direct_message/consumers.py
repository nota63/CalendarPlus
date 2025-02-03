# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from .models import Conversation, Message
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get the conversation_id from the URL
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.conversation = await self.get_conversation()

        if self.conversation:
            self.room_group_name = f'conversation_{self.conversation_id}'

            # Join the conversation room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            # Accept the WebSocket connection
            await self.accept()
        else:
            # Reject connection if conversation doesn't exist
            await self.close()

    async def disconnect(self, close_code):
        # Leave the conversation room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Get the message content from the WebSocket
        text_data_json = json.loads(text_data)
        message_content = text_data_json['message']
        user = self.scope["user"]

        # Save the message to the database
        new_message = await self.save_message(user, message_content)

        # Send the new message to the room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': new_message.content,
                'sender': user.username
            }
        )

    async def chat_message(self, event):
        # Send the message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender']
        }))

    @sync_to_async
    def get_conversation(self):
        # Fetch the conversation asynchronously
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            return conversation
        except Conversation.DoesNotExist:
            return None

    @sync_to_async
    def save_message(self, user, message_content):
        # Save the message to the database asynchronously
        conversation = Conversation.objects.get(id=self.conversation_id)
        # We assume the other user is the receiver
        receiver = conversation.get_other_user(user)
        new_message = Message.objects.create(
            sender=user,
            receiver=receiver,
            conversation=conversation,
            content=message_content
        )
        return new_message
